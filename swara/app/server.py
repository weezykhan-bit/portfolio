"""HTTP API and static web UI. Listens on 127.0.0.1 only; nothing is exposed to the network."""
from __future__ import annotations

import logging
import queue
import threading
import time
import traceback
import uuid
from dataclasses import asdict
from typing import Callable

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, JSONResponse, PlainTextResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from . import __version__, audio, lexicon, store
from .config import (
    APP_NAME, DATA_DIR, MAX_TEXT_CHARS, MAX_UPLOAD_MB, MIN_SAMPLE_SECONDS, PREVIEW_DIR, SAMPLE_RATE,
    UPLOADS_DIR, WEB_DIR, device_label,
)
from .engines import (
    CLONE_LANGUAGES, KOKORO_LANGS, WHISPER_SIZES, Cancelled, EngineManager, GenSettings, preset_voices,
)

log = logging.getLogger("swara")

engines = EngineManager()
gen_lock = threading.Lock()          # one model run at a time on the hardware
PREVIEW_TEXT = {
    "a": "Hi there. This is how I sound when I read your script out loud.",
    "b": "Hello. This is how I sound when I read your script aloud.",
    "h": "नमस्ते। जब मैं आपकी स्क्रिप्ट पढ़ती हूँ, तो मेरी आवाज़ ऐसी लगती है।",
}

app = FastAPI(title=APP_NAME, version=__version__)


# ======================= job queue =======================
ProgressFn = Callable[[int, int], None]


class Job:
    def __init__(self, kind: str, label: str, run: Callable[["Job"], dict]):
        self.id = uuid.uuid4().hex[:12]
        self.kind = kind
        self.label = label
        self.run = run
        self.status = "queued"      # queued | running | done | error | cancelled
        self.done = 0
        self.total = 0
        self.stage = ""
        self.error: str | None = None
        self.result: dict | None = None
        self.cancel = False
        self.created = time.time()
        self.started: float | None = None
        self.finished: float | None = None

    def progress(self, done: int, total: int) -> None:
        self.done, self.total = done, total

    def cancelled(self) -> bool:
        return self.cancel

    def public(self) -> dict:
        end = self.finished or time.time()
        return {
            "id": self.id, "kind": self.kind, "label": self.label, "status": self.status,
            "done": self.done, "total": self.total, "stage": self.stage, "error": self.error,
            "result": self.result, "elapsed": round(end - (self.started or end), 1),
            "position": _queued_ids.index(self.id) + 1 if self.id in _queued_ids else 0,
        }


jobs: dict[str, Job] = {}
job_queue: "queue.Queue[str]" = queue.Queue()
_queued_ids: list[str] = []


def submit(job: Job) -> dict:
    jobs[job.id] = job
    _queued_ids.append(job.id)
    job_queue.put(job.id)
    return job.public()


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
        try:
            with gen_lock:
                job.result = job.run(job)
            job.status = "done"
        except Cancelled:
            job.status = "cancelled"
        except Exception as e:
            log.error("%s job failed: %s", job.kind, traceback.format_exc())
            job.status = "error"
            job.error = str(e) or e.__class__.__name__
        finally:
            job.finished = time.time()
            if len(jobs) > 300:
                for old in sorted(jobs.values(), key=lambda j: j.created)[:100]:
                    if old.status in ("done", "error", "cancelled"):
                        jobs.pop(old.id, None)


threading.Thread(target=_worker, daemon=True, name="swara-worker").start()


# ======================= helpers =======================
@app.exception_handler(HTTPException)
async def http_error(_, exc: HTTPException):
    return JSONResponse({"error": exc.detail}, status_code=exc.status_code)


def _all_voices() -> dict[str, dict]:
    return {v["id"]: v for v in preset_voices() + store.list_voices()}


def _resolve_voice(voice_id: str | None) -> dict:
    if voice_id and voice_id.startswith("clone:"):
        try:
            return store.get_voice(voice_id)
        except KeyError:
            raise HTTPException(404, "That voice no longer exists. Pick another one.")
    v = _all_voices().get(voice_id or "")
    if not v:
        raise HTTPException(404, "That voice no longer exists. Pick another one.")
    return v


def _clone_public(v: dict) -> dict:
    return {k: v[k] for k in v if k not in ("sample_path", "sample_mtime")}


async def _save_upload(file: UploadFile) -> tuple[str, str]:
    name = (file.filename or "audio").replace("\\", "/").split("/")[-1][:120]
    suffix = "." + name.rsplit(".", 1)[-1].lower() if "." in name else ".bin"
    path = UPLOADS_DIR / f"{uuid.uuid4().hex}{suffix[:8]}"
    size = 0
    with open(path, "wb") as fh:
        while chunk := await file.read(1 << 20):
            size += len(chunk)
            if size > MAX_UPLOAD_MB * 1024 * 1024:
                fh.close()
                path.unlink(missing_ok=True)
                raise HTTPException(413, f"File is larger than {MAX_UPLOAD_MB} MB.")
            fh.write(chunk)
    if size == 0:
        path.unlink(missing_ok=True)
        raise HTTPException(400, "The file is empty.")
    return str(path), name


def _download_headers(name: str, download: bool) -> dict:
    return {"Content-Disposition": f'attachment; filename="{name}"'} if download else {}


def _audio_response(wav_path, name: str, fmt: str, download: bool):
    if fmt == "mp3":
        return Response(audio.to_mp3(audio.read_wav(wav_path)), media_type="audio/mpeg",
                        headers=_download_headers(f"{name}.mp3", download))
    return FileResponse(wav_path, media_type="audio/wav", filename=f"{name}.wav" if download else None)


# ======================= status & voices =======================
@app.get("/api/status")
def status():
    return {
        "app": APP_NAME, "version": __version__, "device": engines.device,
        "device_label": device_label(engines.device), "loaded": engines.loaded,
        "busy": any(j.status == "running" for j in jobs.values()), "queued": len(_queued_ids),
        "data_dir": str(DATA_DIR), "max_text_chars": MAX_TEXT_CHARS,
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
    name: str = Form(...), description: str = Form(""), language: str = Form("en"),
    consent: bool = Form(False), file: UploadFile = File(...),
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
        raise HTTPException(400, f"The sample has only {secs:.1f}s of speech. Use at least {MIN_SAMPLE_SECONDS}s (10–30s is best).")
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


# ======================= text to speech =======================
class GenerateRequest(BaseModel):
    text: str = Field(..., min_length=1)
    voice_id: str
    speed: float = Field(1.0, ge=0.5, le=2.0)
    exaggeration: float = Field(0.5, ge=0.0, le=2.0)
    cfg_weight: float = Field(0.5, ge=0.0, le=1.0)
    temperature: float = Field(0.8, ge=0.05, le=2.0)
    seed: int | None = Field(None, ge=0)
    language: str = "en"


def _settings(r) -> GenSettings:
    return GenSettings(speed=r.speed, exaggeration=r.exaggeration, cfg_weight=r.cfg_weight,
                       temperature=r.temperature, seed=r.seed, language=r.language)


@app.post("/api/generate")
def generate(req: GenerateRequest):
    if len(req.text) > MAX_TEXT_CHARS:
        raise HTTPException(400, f"Text is too long (max {MAX_TEXT_CHARS:,} characters per generation).")
    if not req.text.strip():
        raise HTTPException(400, "Enter some text first.")
    voice = _resolve_voice(req.voice_id)
    settings = _settings(req)

    def run(job: Job) -> dict:
        t0 = time.time()
        wav = engines.generate(voice, req.text, settings, job.progress, job.cancelled)
        return store.add_history(wav, {
            "kind": "tts", "text": req.text, "voice_id": voice["id"], "voice_name": voice["name"],
            "voice_kind": voice["kind"], "settings": asdict(settings),
            "render_seconds": round(time.time() - t0, 1), "device": engines.device,
        })

    return submit(Job("tts", voice["name"], run))


# ======================= voice changer =======================
@app.post("/api/changer")
async def voice_changer(voice_id: str = Form(...), file: UploadFile = File(...)):
    target = _resolve_voice(voice_id)
    path, name = await _save_upload(file)

    def run(job: Job) -> dict:
        t0 = time.time()
        try:
            wav = engines.change_voice(path, target, job.progress, job.cancelled)
        finally:
            import os

            os.unlink(path) if os.path.exists(path) else None
        return store.add_history(wav, {
            "kind": "changer", "text": f"Voice changed · {name}", "source_name": name,
            "voice_id": target["id"], "voice_name": target["name"], "voice_kind": target["kind"],
            "settings": {}, "render_seconds": round(time.time() - t0, 1), "device": engines.device,
        })

    return submit(Job("changer", target["name"], run))


# ======================= speech to text =======================
@app.post("/api/transcribe")
async def transcribe(file: UploadFile = File(...), size: str = Form("small"), language: str = Form("")):
    if size not in WHISPER_SIZES:
        raise HTTPException(400, "Unknown accuracy setting.")
    path, name = await _save_upload(file)

    def run(job: Job) -> dict:
        import os

        t0 = time.time()
        try:
            result = engines.transcribe(path, size, language or None, job.progress, job.cancelled)
        except Cancelled:
            raise
        except Exception as e:
            raise RuntimeError(f"Couldn't transcribe this file ({e}). Try an MP3, WAV, M4A or MP4.") from e
        finally:
            os.unlink(path) if os.path.exists(path) else None
        return store.add_transcript({
            **result, "name": name, "model": size, "render_seconds": round(time.time() - t0, 1),
        })

    return submit(Job("transcribe", name, run))


@app.get("/api/transcripts")
def transcripts():
    return {"items": [{k: t[k] for k in ("id", "name", "language", "duration", "created", "render_seconds")}
                      | {"preview": " ".join(s["text"] for s in t["segments"])[:220]}
                      for t in store.list_transcripts()]}


@app.get("/api/transcripts/{tid}")
def transcript(tid: str):
    try:
        return store.get_transcript(tid)
    except KeyError:
        raise HTTPException(404, "Transcript not found")


@app.get("/api/transcripts/{tid}/export")
def transcript_export(tid: str, format: str = "txt"):
    try:
        t = store.get_transcript(tid)
    except KeyError:
        raise HTTPException(404, "Transcript not found")
    base = t["name"].rsplit(".", 1)[0] or "transcript"
    segs = t["segments"]
    if format == "srt":
        body = "\n".join(f"{i}\n{audio.to_srt_time(s['start'])} --> {audio.to_srt_time(s['end'])}\n{s['text']}\n"
                         for i, s in enumerate(segs, 1))
    elif format == "vtt":
        body = "WEBVTT\n\n" + "\n".join(f"{audio.to_srt_time(s['start'], '.')} --> {audio.to_srt_time(s['end'], '.')}\n{s['text']}\n"
                                        for s in segs)
    else:
        format = "txt"
        body = "\n".join(s["text"] for s in segs) + "\n"
    return PlainTextResponse(body, headers=_download_headers(f"{base}.{format}", True))


@app.delete("/api/transcripts/{tid}")
def transcript_delete(tid: str):
    store.delete_transcript(tid)
    return {"ok": True}


# ======================= studio =======================
def _line_state(project: dict, line: dict) -> tuple[str, str | None, str]:
    """Return (status, voice_id, expected_hash) for a line."""
    voice_id = store.voice_for(project, line["speaker"])
    voice = _all_voices().get(voice_id or "") if voice_id else None
    s = project["settings"]
    relevant = {"speed": s["speed"]} if voice and voice["kind"] == "preset" else \
        {k: s[k] for k in ("exaggeration", "cfg_weight", "temperature", "language")}
    h = store.block_hash(line, voice_id, relevant)
    if not line["text"].strip():
        return "empty", voice_id, h
    if not voice:
        return "novoice", voice_id, h
    r = line.get("render")
    if not r:
        return "new", voice_id, h
    return ("ready" if r["hash"] == h else "stale"), voice_id, h


def _project_public(p: dict) -> dict:
    lines = []
    for ln in p["lines"]:
        st, _, _ = _line_state(p, ln)
        lines.append({**ln, "status": st, "duration": (ln.get("render") or {}).get("duration")})
    return {**p, "lines": lines}


class ProjectCreate(BaseModel):
    title: str = ""
    text: str = ""
    voice_id: str = "preset:af_heart"


@app.get("/api/projects")
def projects():
    return {"items": store.list_projects()}


@app.post("/api/projects")
def project_create(body: ProjectCreate):
    _resolve_voice(body.voice_id)
    return _project_public(store.create_project(body.title, body.text, body.voice_id))


@app.get("/api/projects/{pid}")
def project_get(pid: str):
    try:
        return _project_public(store.get_project(pid))
    except KeyError:
        raise HTTPException(404, "Project not found")


@app.put("/api/projects/{pid}")
def project_put(pid: str, body: dict):
    try:
        return _project_public(store.save_project(pid, body))
    except KeyError:
        raise HTTPException(404, "Project not found")


@app.delete("/api/projects/{pid}")
def project_delete(pid: str):
    store.delete_project(pid)
    return {"ok": True}


class RenderRequest(BaseModel):
    line_ids: list[str] | None = None   # None = every line that isn't ready


@app.post("/api/projects/{pid}/render")
def project_render(pid: str, body: RenderRequest):
    try:
        project = store.get_project(pid)
    except KeyError:
        raise HTTPException(404, "Project not found")
    todo = []
    for ln in project["lines"]:
        st, vid, h = _line_state(project, ln)
        if body.line_ids is not None:
            if ln["id"] in body.line_ids and st not in ("empty", "novoice"):
                todo.append((ln["id"], vid, h))
        elif st in ("new", "stale"):
            todo.append((ln["id"], vid, h))
    if not todo:
        raise HTTPException(400, "Every line is already rendered.")
    s = project["settings"]

    def run(job: Job) -> dict:
        done = []
        for i, (lid, vid, h) in enumerate(todo):
            if job.cancelled():
                raise Cancelled()
            job.progress(i, len(todo))
            current = store.get_project(pid)
            line = next((x for x in current["lines"] if x["id"] == lid), None)
            if line is None:
                continue
            voice = _resolve_voice(vid)
            settings = GenSettings(speed=s["speed"], exaggeration=s["exaggeration"], cfg_weight=s["cfg_weight"],
                                   temperature=s["temperature"], language=s["language"])
            wav = engines.generate(voice, line["text"], settings, lambda *_: None, job.cancelled)
            store.set_line_render(pid, lid, h, audio.duration(wav), wav)
            done.append(lid)
            job.progress(i + 1, len(todo))
        return {"project_id": pid, "rendered": done}

    label = "1 line" if len(todo) == 1 else f"{len(todo)} lines"
    return submit(Job("studio", f"{project['title']} · {label}", run))


@app.get("/api/projects/{pid}/lines/{lid}/audio")
def project_line_audio(pid: str, lid: str):
    try:
        return FileResponse(store.line_audio_path(pid, lid), media_type="audio/wav")
    except KeyError:
        raise HTTPException(404, "This line hasn't been rendered yet.")


@app.get("/api/projects/{pid}/export")
def project_export(pid: str, format: str = "wav", download: bool = True):
    try:
        p = store.get_project(pid)
    except KeyError:
        raise HTTPException(404, "Project not found")
    chunks, gaps, missing = [], [], 0
    for ln in p["lines"]:
        st, _, _ = _line_state(p, ln)
        if st == "empty":
            continue
        if st != "ready":
            missing += 1
            continue
        chunks.append(audio.read_wav(store.line_audio_path(pid, ln["id"])))
        gaps.append(ln.get("pause", 0.5))
    if missing:
        raise HTTPException(400, f"{missing} line(s) aren't rendered yet. Render all lines, then export.")
    if not chunks:
        raise HTTPException(400, "Nothing to export yet.")
    wav = audio.join(chunks, gaps)
    name = "".join(c for c in p["title"] if c.isalnum() or c in " -_").strip() or "project"
    if format == "mp3":
        return Response(audio.to_mp3(wav), media_type="audio/mpeg", headers=_download_headers(f"{name}.mp3", download))
    tmp = audio.tmp_path(".wav")
    audio.write_wav(tmp, wav)
    data = tmp.read_bytes()
    tmp.unlink(missing_ok=True)
    return Response(data, media_type="audio/wav", headers=_download_headers(f"{name}.wav", download))


# ======================= pronunciations =======================
@app.get("/api/pronunciations")
def pronunciations():
    return {"items": lexicon.load()}


@app.put("/api/pronunciations")
def pronunciations_put(body: dict):
    return {"items": lexicon.save(body.get("items", []))}


class PreviewText(BaseModel):
    text: str


@app.post("/api/pronunciations/apply")
def pronunciations_apply(body: PreviewText):
    return {"text": lexicon.apply(body.text)}


# ======================= jobs & history =======================
@app.get("/api/jobs")
def jobs_list():
    active = [j for j in jobs.values() if j.status in ("queued", "running")]
    return {"items": [j.public() for j in sorted(active, key=lambda j: j.created)]}


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
    return _audio_response(path, f"swara-{hid}", format, download)


@app.delete("/api/history/{hid}")
def history_delete(hid: str):
    try:
        store.delete_history(hid)
    except KeyError:
        raise HTTPException(404, "Not found")
    return {"ok": True}


app.mount("/", StaticFiles(directory=WEB_DIR, html=True), name="web")
