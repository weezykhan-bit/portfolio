"""On-disk storage for cloned voices and generation history.

Layout (inside DATA_DIR, by default ``voice-studio/data``)::

    voices/<id>/meta.json      name, description, language, created
    voices/<id>/sample.wav     cleaned reference clip (24 kHz mono)
    history/<id>.json          text, voice, settings, duration
    history/<id>.wav           generated audio
"""
from __future__ import annotations

import json
import shutil
import threading
import time
import uuid
from pathlib import Path

import numpy as np

from . import audio
from .config import HISTORY_DIR, PROJECTS_DIR, TRANSCRIPTS_DIR, VOICES_DIR

_lock = threading.Lock()


def _new_id() -> str:
    return time.strftime("%Y%m%d-%H%M%S-") + uuid.uuid4().hex[:6]


def _safe_id(item_id: str) -> str:
    if not item_id or "/" in item_id or "\\" in item_id or ".." in item_id:
        raise KeyError(item_id)
    return item_id


def _read_json(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))


def _write_json(p: Path, data: dict) -> None:
    tmp = p.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(p)


# ---------------- voices ----------------
def _voice_public(vdir: Path) -> dict:
    meta = _read_json(vdir / "meta.json")
    sample = vdir / "sample.wav"
    meta.update(
        id=f"clone:{vdir.name}",
        kind="clone",
        sample_path=str(sample),
        sample_mtime=sample.stat().st_mtime if sample.exists() else None,
    )
    return meta


def list_voices() -> list[dict]:
    out = []
    for vdir in sorted(VOICES_DIR.iterdir(), reverse=True):
        if (vdir / "meta.json").exists() and (vdir / "sample.wav").exists():
            try:
                out.append(_voice_public(vdir))
            except Exception:
                continue
    return out


def get_voice(voice_id: str) -> dict:
    vdir = VOICES_DIR / _safe_id(voice_id.split(":", 1)[-1])
    if not (vdir / "meta.json").exists():
        raise KeyError(voice_id)
    return _voice_public(vdir)


def create_voice(name: str, description: str, language: str, sample: np.ndarray) -> dict:
    vid = _new_id()
    vdir = VOICES_DIR / vid
    vdir.mkdir(parents=True)
    audio.write_wav(vdir / "sample.wav", sample)
    _write_json(
        vdir / "meta.json",
        {
            "name": name.strip()[:60] or "Untitled voice",
            "description": description.strip()[:240],
            "language": language,
            "created": time.time(),
            "sample_seconds": audio.duration(sample),
        },
    )
    return _voice_public(vdir)


def update_voice(voice_id: str, **fields) -> dict:
    vdir = VOICES_DIR / _safe_id(voice_id.split(":", 1)[-1])
    with _lock:
        meta = _read_json(vdir / "meta.json")
        for k in ("name", "description", "language"):
            if fields.get(k) is not None:
                meta[k] = str(fields[k]).strip()[:240]
        _write_json(vdir / "meta.json", meta)
    return _voice_public(vdir)


def delete_voice(voice_id: str) -> None:
    vdir = VOICES_DIR / _safe_id(voice_id.split(":", 1)[-1])
    if vdir.exists():
        shutil.rmtree(vdir)


# ---------------- history ----------------
def add_history(wav: np.ndarray, record: dict) -> dict:
    hid = _new_id()
    audio.write_wav(HISTORY_DIR / f"{hid}.wav", wav)
    record = {**record, "id": hid, "created": time.time(), "duration": audio.duration(wav)}
    _write_json(HISTORY_DIR / f"{hid}.json", record)
    return record


def list_history(limit: int = 200) -> list[dict]:
    items = []
    for p in sorted(HISTORY_DIR.glob("*.json"), reverse=True)[:limit]:
        try:
            items.append(_read_json(p))
        except Exception:
            continue
    return items


def history_audio_path(hid: str) -> Path:
    p = HISTORY_DIR / f"{_safe_id(hid)}.wav"
    if not p.exists():
        raise KeyError(hid)
    return p


def delete_history(hid: str) -> None:
    for ext in (".wav", ".json"):
        (HISTORY_DIR / f"{_safe_id(hid)}{ext}").unlink(missing_ok=True)


# ---------------- studio projects ----------------
# A project is a script: an ordered list of lines, each spoken by a speaker
# from the project's cast. The cast maps speaker names to voices, so recasting
# a character re-voices every line they speak.
import hashlib
import re as _re

_SPEAKER_RE = _re.compile(r"^\s*([A-Za-zऀ-ॿ][\wऀ-ॿ .'-]{0,30}?)\s*:\s+(.+)$")


def _pdir(pid: str) -> Path:
    return PROJECTS_DIR / _safe_id(pid)


def parse_script(text: str, default_speaker: str = "Narrator") -> tuple[list[dict], list[str]]:
    """Split pasted text into lines. ``NAME: words`` lines become dialogue for NAME;
    everything else is a paragraph for the default speaker."""
    lines, speakers = [], []
    canonical: dict[str, str] = {}  # "riya" -> "Riya": first spelling wins
    for raw in text.replace("\r\n", "\n").split("\n"):
        raw = raw.strip()
        if not raw:
            continue
        m = _SPEAKER_RE.match(raw)
        speaker, words = (m.group(1).strip(), m.group(2).strip()) if m and len(m.group(1).split()) <= 3 else (default_speaker, raw)
        speaker = canonical.setdefault(speaker.lower(), speaker)
        if speaker not in speakers:
            speakers.append(speaker)
        lines.append({"id": uuid.uuid4().hex[:10], "speaker": speaker, "text": words, "pause": 0.5, "render": None})
    return lines, speakers


def block_hash(block: dict, voice_id: str | None, settings: dict) -> str:
    key = json.dumps([block.get("text", ""), voice_id, settings, block.get("speed")], sort_keys=True, ensure_ascii=False)
    return hashlib.sha1(key.encode("utf-8")).hexdigest()[:16]


DEFAULT_PROJECT_SETTINGS = {"exaggeration": 0.5, "cfg_weight": 0.5, "temperature": 0.8, "speed": 1.0, "language": "en"}


def create_project(title: str, text: str, default_voice: str) -> dict:
    pid = _new_id()
    _pdir(pid).mkdir(parents=True)
    lines, speakers = parse_script(text)
    if not lines:
        lines = [{"id": uuid.uuid4().hex[:10], "speaker": "Narrator", "text": "", "pause": 0.5, "render": None}]
        speakers = ["Narrator"]
    project = {
        "id": pid,
        "title": title.strip()[:120] or "Untitled project",
        "created": time.time(),
        "updated": time.time(),
        "cast": [{"speaker": s, "voice_id": default_voice} for s in speakers],
        "settings": dict(DEFAULT_PROJECT_SETTINGS),
        "lines": lines,
    }
    _write_json(_pdir(pid) / "project.json", project)
    return project


def get_project(pid: str) -> dict:
    p = _pdir(pid) / "project.json"
    if not p.exists():
        raise KeyError(pid)
    return _read_json(p)


def voice_for(project: dict, speaker: str) -> str | None:
    for c in project.get("cast", []):
        if c["speaker"] == speaker:
            return c["voice_id"]
    return None


def save_project(pid: str, incoming: dict) -> dict:
    """Replace a project's editable fields, keeping render info only for lines
    whose text, voice and settings are unchanged."""
    with _lock:
        current = get_project(pid)
        old = {ln["id"]: ln for ln in current["lines"]}
        cast = [
            {"speaker": str(c.get("speaker", "")).strip()[:40] or "Narrator", "voice_id": str(c.get("voice_id", ""))}
            for c in incoming.get("cast", current["cast"])
        ]
        settings = {**DEFAULT_PROJECT_SETTINGS, **{k: incoming.get("settings", {}).get(k, v) for k, v in current["settings"].items()}}
        lines = []
        for ln in incoming.get("lines", current["lines"]):
            lid = _safe_id(str(ln.get("id") or uuid.uuid4().hex[:10]))
            new = {
                "id": lid,
                "speaker": str(ln.get("speaker", "Narrator"))[:40],
                "text": str(ln.get("text", ""))[:5000],
                "pause": max(0.0, min(5.0, float(ln.get("pause", 0.5)))),
                "render": None,
            }
            prev = old.get(lid)
            if prev and prev.get("render"):
                new["render"] = prev["render"]  # staleness is computed on read
            lines.append(new)
        # delete audio for removed lines
        keep = {ln["id"] for ln in lines}
        for lid in set(old) - keep:
            (_pdir(pid) / f"{lid}.wav").unlink(missing_ok=True)
        current.update(
            title=str(incoming.get("title", current["title"])).strip()[:120] or "Untitled project",
            cast=cast, settings=settings, lines=lines, updated=time.time(),
        )
        _write_json(_pdir(pid) / "project.json", current)
    return current


def set_line_render(pid: str, lid: str, h: str, duration: float, wav: np.ndarray) -> None:
    audio.write_wav(_pdir(pid) / f"{_safe_id(lid)}.wav", wav)
    with _lock:
        project = get_project(pid)
        for ln in project["lines"]:
            if ln["id"] == lid:
                ln["render"] = {"hash": h, "duration": duration, "at": time.time()}
        _write_json(_pdir(pid) / "project.json", project)


def line_audio_path(pid: str, lid: str) -> Path:
    p = _pdir(pid) / f"{_safe_id(lid)}.wav"
    if not p.exists():
        raise KeyError(lid)
    return p


def list_projects() -> list[dict]:
    out = []
    for d in sorted(PROJECTS_DIR.iterdir(), reverse=True):
        try:
            p = _read_json(d / "project.json")
        except Exception:
            continue
        words = sum(len(ln["text"].split()) for ln in p["lines"])
        out.append({
            "id": p["id"], "title": p["title"], "updated": p["updated"], "lines": len(p["lines"]),
            "words": words, "speakers": [c["speaker"] for c in p["cast"]],
            "rendered": sum(1 for ln in p["lines"] if ln.get("render")),
        })
    return sorted(out, key=lambda x: -x["updated"])


def delete_project(pid: str) -> None:
    d = _pdir(pid)
    if d.exists():
        shutil.rmtree(d)


# ---------------- transcripts ----------------
def add_transcript(record: dict) -> dict:
    tid = _new_id()
    record = {**record, "id": tid, "created": time.time()}
    _write_json(TRANSCRIPTS_DIR / f"{tid}.json", record)
    return record


def list_transcripts() -> list[dict]:
    out = []
    for p in sorted(TRANSCRIPTS_DIR.glob("*.json"), reverse=True)[:200]:
        try:
            out.append(_read_json(p))
        except Exception:
            continue
    return out


def get_transcript(tid: str) -> dict:
    p = TRANSCRIPTS_DIR / f"{_safe_id(tid)}.json"
    if not p.exists():
        raise KeyError(tid)
    return _read_json(p)


def delete_transcript(tid: str) -> None:
    (TRANSCRIPTS_DIR / f"{_safe_id(tid)}.json").unlink(missing_ok=True)
