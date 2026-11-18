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
from .config import HISTORY_DIR, VOICES_DIR

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
