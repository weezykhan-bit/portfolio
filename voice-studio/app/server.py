"""HTTP API and static web UI. Everything runs on 127.0.0.1 only."""
from __future__ import annotations

import logging
import queue
import threading
import time
import traceback
import uuid
from dataclasses import asdict

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from . import __version__, audio, store
from .config import DATA_DIR, MAX_TEXT_CHARS, MIN_SAMPLE_SECONDS, SAMPLE_RATE, WEB_DIR, device_label
from .engines import CLONE_LANGUAGES, KOKORO_LANGS, Cancelled, EngineManager, GenSettings, preset_voices

log = logging.getLogger("voice_studio")

engines = EngineManager()
gen_lock = threading.Lock()          # one generation at a time on the hardware
PREVIEW_DIR = DATA_DIR / "previews"
PREVIEW_DIR.mkdir(parents=True, exist_ok=True)
PREVIEW_TEXT = {
    "a": "Hi there. This is how I sound when I read your script out loud.",
    "b": "Hello. This is how I sound when I read your script aloud.",
    "h": "नमस्ते। जब मैं आपकी स्क्रिप्ट पढ़ती हूँ, तो मेरी आवाज़ ऐसी लगती है।",
}

app = FastAPI(title="Local Voice Studio", version=__version__)


# ---------------- jobs ----------------
class Job:
    def __init__(self, req: "GenerateRequest", voice: dict):
        self.id = uuid.uuid4().hex[:12]
        self.req = req
        self.voice = voice
        self.status = "queued"      # queued | running | done | error | cancelled
        self.done = 0
        self.total = 0
        self.error: str | None = None
        self.result: dict | None = None
        self.cancel = False
        self.created = time.time()
        self.started: float | None = None

    def public(self) -> dict:
        return {
            "id": self.id,
            "status": self.status,
            "done": self.done,
            "total": self.total,
            "error": self.error,
            "result": self.result,
            "elapsed": round(time.time() - (self.started or time.time()), 1),
            "position": _queue_position(self.id),
        }


jobs: dict[str, Job] = {}
job_queue: "queue.Queue[str]" = queue.Queue()
_queued_ids: list[str] = []


def _queue_position(jid: str) -> int:
    try:
        return _queued_ids.index(jid) + 1
    except ValueError:
        return 0


def _worker() -> None:
    while True:
        jid = job_queue.get()
        if jid in _queued_ids:
            _queued_ids.remove(jid)
        job = jobs.get(jid)
        if job is None or job.cancel:
            if job:
                job.status = "cancelled"
            continue
        job.status = "running"
        job.started = time.time()
        r = job.req
        settings = GenSettings(
            speed=r.speed, exaggeration=r.exaggeration, cfg_weight=r.cfg_weight,
            temperature=r.temperature, seed=r.seed, language=r.language,
        )

        def progress(done: int, total: int) -> None:
            job.done, job.total = done, total

        try:
            with gen_lock:
                wav = engines.generate(job.voice, r.text, settings, progress, lambda: job.cancel)
            record = store.add_history(
                wav,
                {
                    "text": r.text,
                    "voice_id": job.voice["id"],
                    "voice_name": job.voice["name"],
                    "voice_kind": job.voice["kind"],
                    "settings": asdict(settings),
                    "render_seconds": round(time.time() - job.started, 1),
                    "device": engines.device,
                },
            )
            job.result = record
            job.status = "done"
        except Cancelled:
            job.status = "cancelled"
        except Exception as e:  # surface the error in the UI
            log.error("Generation failed: %s", traceback.format_exc())
            job.status = "error"
            job.error = str(e) or e.__class__.__name__
        finally:
            # keep memory bounded: forget old finished jobs
            if len(jobs) > 200:
                for old in sorted(jobs.values(), key=lambda j: j.created)[:50]:
                    if old.status in ("done", "error", "cancelled"):
                        jobs.pop(old.id, None)


threading.Thread(target=_worker, daemon=True, name="tts-worker").start()


# ---------------- API ----------------
def _all_voices() -> dict[str, dict]:
    return {v["id"]: v for v in preset_voices() + store.list_voices()}


def _resolve_voice(voice_id: str) -> dict:
    if voice_id.startswith("clone:"):
        try:
            return store.get_voice(voice_id)
        except KeyError:
            raise HTTPException(404, "Voice not found")
    v = _all_voices().get(voice_id)
    if not v:
        raise HTTPException(404, "Voice not found")
    return v


def _clone_public(v: dict) -> dict:
    return {k: v[k] for k in v if k not in ("sample_path", "sample_mtime")}


@app.get("/api/status")
def status():
    running = [j for j in jobs.values() if j.status == "running"]
    return {
        "version": __version__,
        "device": engines.device,
        "device_label": device_label(engines.device),
        "loaded": engines.loaded,
        "busy": bool(running),
        "queued": len(_queued_ids),
        "data_dir": str(DATA_DIR),
        "max_text_chars": MAX_TEXT_CHARS,
    }


@app.get("/api/voices")
def voices():
    return {
        "presets": preset_voices(),
        "clones": [_clone_public(v) for v in store.list_voices()],
        "clone_languages": CLONE_LANGUAGES,
        "preset_languages": {k: v[0] for k, v in KOKORO_LANGS.items()},
    }


@app.post("/api/voices")
async def create_voice(
    name: str = Form(...),
    description: str = Form(""),
    language: str = Form("en"),
    consent: bool = Form(False),
    file: UploadFile = File(...),
):
    if not consent:
        raise HTTPException(400, "Please confirm you have the right to use this voice.")
    data = await file.read()
    if len(data) > 50 * 1024 * 1024:
        raise HTTPException(413, "File too large (max 50 MB).")
    try:
        wav = audio.load_sample(data)
    except Exception:
        raise HTTPException(400, "Couldn't read that audio file. Try WAV, MP3, M4A or a new recording.")
    secs = len(wav) / SAMPLE_RATE
    if secs < MIN_SAMPLE_SECONDS:
        raise HTTPException(
            400, f"The sample has only {secs:.1f}s of speech. Use at least {MIN_SAMPLE_SECONDS}s (10–30s is best)."
        )
    v = store.create_voice(name, description, language if language in CLONE_LANGUAGES else "en", wav)
    return _clone_public(v)


class VoicePatch(BaseModel):
    name: str | None = None
    description: str | None = None
    language: str | None = None


@app.patch("/api/voices/{voice_id}")
def patch_voice(voice_id: str, body: VoicePatch):
    try:
        return _clone_public(store.update_voice(voice_id, **body.model_dump()))
    except (KeyError, FileNotFoundError):
        raise HTTPException(404, "Voice not found")


@app.delete("/api/voices/{voice_id}")
def delete_voice(voice_id: str):
    try:
        store.delete_voice(voice_id)
    except KeyError:
        raise HTTPException(404, "Voice not found")
    return {"ok": True}


@app.get("/api/voices/{voice_id}/preview")
def voice_preview(voice_id: str):
    v = _resolve_voice(voice_id)
    if v["kind"] == "clone":
        return FileResponse(v["sample_path"], media_type="audio/wav")
    vid = voice_id.split(":", 1)[1]
    path = PREVIEW_DIR / f"{vid}.wav"
    if not path.exists():
        with gen_lock:
            wav = engines.generate(v, PREVIEW_TEXT[v["lang_code"]], GenSettings(), lambda *_: None, lambda: False)
        audio.write_wav(path, wav)
    return FileResponse(path, media_type="audio/wav")


class GenerateRequest(BaseModel):
    text: str = Field(..., min_length=1)
    voice_id: str
    speed: float = Field(1.0, ge=0.5, le=2.0)
    exaggeration: float = Field(0.5, ge=0.0, le=2.0)
    cfg_weight: float = Field(0.5, ge=0.0, le=1.0)
    temperature: float = Field(0.8, ge=0.05, le=2.0)
    seed: int | None = Field(None, ge=0)
    language: str = "en"


@app.post("/api/generate")
def generate(req: GenerateRequest):
    if len(req.text) > MAX_TEXT_CHARS:
        raise HTTPException(400, f"Text is too long (max {MAX_TEXT_CHARS:,} characters per generation).")
    if not req.text.strip():
        raise HTTPException(400, "Enter some text first.")
    voice = _resolve_voice(req.voice_id)
    job = Job(req, voice)
    jobs[job.id] = job
    _queued_ids.append(job.id)
    job_queue.put(job.id)
    return job.public()


@app.get("/api/jobs/{job_id}")
def job_status(job_id: str):
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(404, "Job not found")
    return job.public()


@app.post("/api/jobs/{job_id}/cancel")
def job_cancel(job_id: str):
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(404, "Job not found")
    job.cancel = True
    if job.status == "queued":
        job.status = "cancelled"
    return job.public()


@app.get("/api/history")
def history():
    return {"items": store.list_history()}


@app.get("/api/history/{hid}/audio")
def history_audio(hid: str, format: str = "wav", download: bool = False):
    try:
        path = store.history_audio_path(hid)
    except KeyError:
        raise HTTPException(404, "Not found")
    name = f"voice-studio-{hid}"
    if format == "mp3":
        data = audio.to_mp3(audio.read_wav(path))
        headers = {"Content-Disposition": f'attachment; filename="{name}.mp3"'} if download else {}
        return Response(data, media_type="audio/mpeg", headers=headers)
    return FileResponse(path, media_type="audio/wav", filename=f"{name}.wav" if download else None)


@app.delete("/api/history/{hid}")
def history_delete(hid: str):
    try:
        store.delete_history(hid)
    except KeyError:
        raise HTTPException(404, "Not found")
    return {"ok": True}


@app.exception_handler(HTTPException)
async def http_error(_, exc: HTTPException):
    return JSONResponse({"error": exc.detail}, status_code=exc.status_code)


app.mount("/", StaticFiles(directory=WEB_DIR, html=True), name="web")
