"""Paths and hardware detection."""
from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WEB_DIR = ROOT / "web"
DATA_DIR = Path(os.environ.get("VOICE_STUDIO_DATA", ROOT / "data")).resolve()
VOICES_DIR = DATA_DIR / "voices"
HISTORY_DIR = DATA_DIR / "history"

SAMPLE_RATE = 24000          # both engines output 24 kHz
MAX_TEXT_CHARS = 20000       # per generation request
MAX_SAMPLE_SECONDS = 40      # longer reference clips are trimmed
MIN_SAMPLE_SECONDS = 5

for d in (VOICES_DIR, HISTORY_DIR):
    d.mkdir(parents=True, exist_ok=True)


def detect_device() -> str:
    """Pick the fastest available backend: NVIDIA GPU, Apple Silicon GPU, or CPU."""
    forced = os.environ.get("VOICE_STUDIO_DEVICE")
    if forced:
        return forced
    import torch

    if torch.cuda.is_available():
        return "cuda"
    if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
        return "mps"
    return "cpu"


def device_label(device: str) -> str:
    if device == "cuda":
        import torch

        return f"NVIDIA GPU ({torch.cuda.get_device_name(0)})"
    if device == "mps":
        return "Apple Silicon GPU"
    return f"CPU ({os.cpu_count()} cores)"
