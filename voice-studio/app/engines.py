"""Speech engines.

* Kokoro (Apache-2.0): fast built-in voices, runs well on CPU.
* Chatterbox (MIT, Resemble AI): zero-shot voice cloning from a short sample.
  The English model is used for English; the multilingual model covers 23
  languages including Hindi.

Models download once from Hugging Face on first use (or via ``prefetch``) and
are then loaded from the local cache, so the app works offline afterwards.
"""
from __future__ import annotations

import gc
import logging
import threading
from dataclasses import dataclass
from typing import Callable

import numpy as np

from . import audio
from .config import SAMPLE_RATE, detect_device
from .textproc import chunk_with_pauses

log = logging.getLogger("voice_studio.engines")

KOKORO_REPO = "hexgrad/Kokoro-82M"

# lang code -> (label, list of (voice_id, display name, gender))
KOKORO_LANGS: dict[str, tuple[str, list[tuple[str, str, str]]]] = {
    "a": (
        "English (US)",
        [
            ("af_heart", "Heart", "female"),
            ("af_bella", "Bella", "female"),
            ("af_nicole", "Nicole", "female"),
            ("af_sarah", "Sarah", "female"),
            ("af_sky", "Sky", "female"),
            ("af_nova", "Nova", "female"),
            ("af_aoede", "Aoede", "female"),
            ("af_kore", "Kore", "female"),
            ("am_michael", "Michael", "male"),
            ("am_fenrir", "Fenrir", "male"),
            ("am_puck", "Puck", "male"),
            ("am_adam", "Adam", "male"),
            ("am_echo", "Echo", "male"),
            ("am_eric", "Eric", "male"),
            ("am_liam", "Liam", "male"),
            ("am_onyx", "Onyx", "male"),
        ],
    ),
    "b": (
        "English (UK)",
        [
            ("bf_emma", "Emma", "female"),
            ("bf_isabella", "Isabella", "female"),
            ("bf_alice", "Alice", "female"),
            ("bf_lily", "Lily", "female"),
            ("bm_george", "George", "male"),
            ("bm_fable", "Fable", "male"),
            ("bm_daniel", "Daniel", "male"),
            ("bm_lewis", "Lewis", "male"),
        ],
    ),
    "h": (
        "Hindi",
        [
            ("hf_alpha", "Ananya", "female"),
            ("hf_beta", "Bhavna", "female"),
            ("hm_omega", "Omkar", "male"),
            ("hm_psi", "Pranav", "male"),
        ],
    ),
}

CLONE_LANGUAGES = {
    "en": "English", "hi": "Hindi", "ar": "Arabic", "da": "Danish", "de": "German",
    "el": "Greek", "es": "Spanish", "fi": "Finnish", "fr": "French", "he": "Hebrew",
    "it": "Italian", "ja": "Japanese", "ko": "Korean", "ms": "Malay", "nl": "Dutch",
    "no": "Norwegian", "pl": "Polish", "pt": "Portuguese", "ru": "Russian",
    "sv": "Swedish", "sw": "Swahili", "tr": "Turkish", "zh": "Chinese",
}


def preset_voices() -> list[dict]:
    out = []
    for lang, (label, voices) in KOKORO_LANGS.items():
        for vid, name, gender in voices:
            out.append(
                {
                    "id": f"preset:{vid}",
                    "name": name,
                    "kind": "preset",
                    "gender": gender,
                    "language": label,
                    "lang_code": lang,
                }
            )
    return out


class Cancelled(Exception):
    pass


@dataclass
class GenSettings:
    speed: float = 1.0          # Kokoro only
    exaggeration: float = 0.5   # Chatterbox: emotion intensity
    cfg_weight: float = 0.5     # Chatterbox: lower = slower, more deliberate pacing
    temperature: float = 0.8    # Chatterbox: variation between takes
    seed: int | None = None
    language: str = "en"        # Chatterbox language for cloned voices


ProgressFn = Callable[[int, int], None]
CancelFn = Callable[[], bool]


class EngineManager:
    """Loads models lazily and keeps at most one cloning model in memory."""

    def __init__(self) -> None:
        self.device = detect_device()
        self._lock = threading.RLock()
        self._kokoro_model = None
        self._kokoro_pipes: dict[str, object] = {}
        self._clone_kind: str | None = None   # "en" or "multi"
        self._clone_model = None
        self._conds_key: tuple | None = None
        self.loaded: dict[str, bool] = {"kokoro": False, "clone_en": False, "clone_multi": False}

    # ---------- Kokoro ----------
    def _kokoro(self, lang: str):
        with self._lock:
            if lang in self._kokoro_pipes:
                return self._kokoro_pipes[lang]
            from kokoro import KModel, KPipeline

            if self._kokoro_model is None:
                log.info("Loading Kokoro on %s", self.device)
                # Kokoro's MPS support is partial; CPU is fast enough for an 82M model.
                dev = "cuda" if self.device == "cuda" else "cpu"
                self._kokoro_model = KModel(repo_id=KOKORO_REPO).to(dev).eval()
                self.loaded["kokoro"] = True
            pipe = KPipeline(lang_code=lang, repo_id=KOKORO_REPO, model=self._kokoro_model)
            self._kokoro_pipes[lang] = pipe
            return pipe

    def _gen_kokoro(self, voice: dict, text: str, s: GenSettings, progress: ProgressFn, cancelled: CancelFn) -> np.ndarray:
        pipe = self._kokoro(voice["lang_code"])
        vid = voice["id"].split(":", 1)[1]
        pieces = chunk_with_pauses(text, max_chars=400)
        chunks, gaps = [], []
        for i, (piece, pause) in enumerate(pieces):
            if cancelled():
                raise Cancelled()
            segs = [a.numpy() if hasattr(a, "numpy") else np.asarray(a)
                    for _, _, a in pipe(piece, voice=vid, speed=s.speed) if a is not None]
            if segs:
                chunks.append(np.concatenate(segs))
                gaps.append(pause / max(s.speed, 0.5))
            progress(i + 1, len(pieces))
        return audio.join(chunks, gaps)

    # ---------- Chatterbox ----------
    def _clone(self, kind: str):
        with self._lock:
            if self._clone_kind == kind and self._clone_model is not None:
                return self._clone_model
            self._unload_clone()
            log.info("Loading Chatterbox (%s) on %s", kind, self.device)
            if kind == "en":
                from chatterbox.tts import ChatterboxTTS

                self._clone_model = ChatterboxTTS.from_pretrained(device=self.device)
            else:
                from chatterbox.mtl_tts import ChatterboxMultilingualTTS

                self._clone_model = ChatterboxMultilingualTTS.from_pretrained(device=self.device)
            self._clone_kind = kind
            self.loaded["clone_en" if kind == "en" else "clone_multi"] = True
            return self._clone_model

    def _unload_clone(self) -> None:
        if self._clone_model is None:
            return
        self._clone_model = None
        self._conds_key = None
        self.loaded["clone_en"] = self.loaded["clone_multi"] = False
        self._clone_kind = None
        gc.collect()
        try:
            import torch

            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        except Exception:
            pass

    def _gen_clone(self, voice: dict, text: str, s: GenSettings, progress: ProgressFn, cancelled: CancelFn) -> np.ndarray:
        lang = s.language if s.language in CLONE_LANGUAGES else "en"
        kind = "en" if lang == "en" else "multi"
        model = self._clone(kind)
        key = (kind, voice["id"], voice.get("sample_mtime"))
        if self._conds_key != key:
            model.prepare_conditionals(voice["sample_path"], exaggeration=s.exaggeration)
            self._conds_key = key
        pieces = chunk_with_pauses(text, max_chars=260 if lang == "en" else 200)
        chunks, gaps = [], []
        for i, (piece, pause) in enumerate(pieces):
            if cancelled():
                raise Cancelled()
            kwargs = dict(exaggeration=s.exaggeration, cfg_weight=s.cfg_weight, temperature=s.temperature)
            if kind == "multi":
                kwargs["language_id"] = lang
            wav = model.generate(piece, **kwargs)
            chunks.append(wav.squeeze(0).detach().cpu().numpy().astype(np.float32))
            gaps.append(pause)
            progress(i + 1, len(pieces))
        return audio.join(chunks, gaps)

    # ---------- public ----------
    def generate(self, voice: dict, text: str, s: GenSettings, progress: ProgressFn, cancelled: CancelFn) -> np.ndarray:
        if s.seed is not None:
            import random

            import torch

            torch.manual_seed(s.seed)
            np.random.seed(s.seed % (2**32))
            random.seed(s.seed)
        if voice["kind"] == "preset":
            wav = self._gen_kokoro(voice, text, s, progress, cancelled)
        else:
            wav = self._gen_clone(voice, text, s, progress, cancelled)
        return audio.peak_normalize(wav, 0.92)

    def warm(self, which: list[str]) -> None:
        """Download (if needed) and load models, used by prefetch."""
        if "kokoro" in which:
            for lang in KOKORO_LANGS:
                pipe = self._kokoro(lang)
                for vid, _, _ in KOKORO_LANGS[lang][1]:
                    pipe.load_voice(vid)
        if "clone_en" in which:
            self._clone("en")
        if "clone_multi" in which:
            self._clone("multi")


assert SAMPLE_RATE == 24000  # both engines emit 24 kHz audio
