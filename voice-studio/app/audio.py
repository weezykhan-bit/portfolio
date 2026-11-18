"""Audio helpers: loading voice samples, stitching chunks, exporting WAV/MP3."""
from __future__ import annotations

import io
from pathlib import Path

import numpy as np
import soundfile as sf

from .config import MAX_SAMPLE_SECONDS, SAMPLE_RATE


def load_sample(data: bytes) -> np.ndarray:
    """Decode an uploaded voice sample to mono float32 at SAMPLE_RATE.

    The browser converts recordings and most formats to WAV before upload, so
    soundfile handles nearly everything; librosa is the fallback for the rest.
    """
    try:
        wav, sr = sf.read(io.BytesIO(data), dtype="float32", always_2d=True)
        wav = wav.mean(axis=1)
    except Exception:
        import librosa

        wav, sr = librosa.load(io.BytesIO(data), sr=None, mono=True)
    if sr != SAMPLE_RATE:
        import librosa

        wav = librosa.resample(wav, orig_sr=sr, target_sr=SAMPLE_RATE)
    wav = trim_silence(wav)
    wav = wav[: MAX_SAMPLE_SECONDS * SAMPLE_RATE]
    return peak_normalize(wav, 0.95)


def trim_silence(wav: np.ndarray, threshold_db: float = -45.0) -> np.ndarray:
    if wav.size == 0:
        return wav
    frame = int(0.02 * SAMPLE_RATE)
    n = len(wav) // frame
    if n == 0:
        return wav
    rms = np.sqrt(np.mean(wav[: n * frame].reshape(n, frame) ** 2, axis=1) + 1e-12)
    db = 20 * np.log10(rms)
    voiced = np.where(db > threshold_db)[0]
    if voiced.size == 0:
        return wav
    start = max(0, (voiced[0] - 5) * frame)
    end = min(len(wav), (voiced[-1] + 6) * frame)
    return wav[start:end]


def peak_normalize(wav: np.ndarray, peak: float = 0.9) -> np.ndarray:
    m = float(np.max(np.abs(wav))) if wav.size else 0.0
    if m < 1e-6:
        return wav
    return (wav / m * peak).astype(np.float32)


def join(chunks: list[np.ndarray], gaps: list[float]) -> np.ndarray:
    """Concatenate chunks, inserting ``gaps[i]`` seconds of silence after chunk i,
    with short fades so joins don't click."""
    out: list[np.ndarray] = []
    fade = int(0.008 * SAMPLE_RATE)
    for i, c in enumerate(chunks):
        c = np.asarray(c, dtype=np.float32).copy()
        if len(c) > 2 * fade:
            ramp = np.linspace(0.0, 1.0, fade, dtype=np.float32)
            c[:fade] *= ramp
            c[-fade:] *= ramp[::-1]
        out.append(c)
        if i < len(chunks) - 1:
            out.append(np.zeros(int(gaps[i] * SAMPLE_RATE), dtype=np.float32))
    return np.concatenate(out) if out else np.zeros(0, dtype=np.float32)


def write_wav(path: Path, wav: np.ndarray) -> None:
    sf.write(str(path), wav, SAMPLE_RATE, subtype="PCM_16")


def to_mp3(wav: np.ndarray, bitrate: int = 192) -> bytes:
    import lameenc

    pcm = (np.clip(wav, -1.0, 1.0) * 32767).astype(np.int16).tobytes()
    enc = lameenc.Encoder()
    enc.set_bit_rate(bitrate)
    enc.set_in_sample_rate(SAMPLE_RATE)
    enc.set_channels(1)
    enc.set_quality(2)
    return bytes(enc.encode(pcm) + enc.flush())


def read_wav(path: Path) -> np.ndarray:
    wav, _ = sf.read(str(path), dtype="float32")
    return wav


def duration(wav: np.ndarray) -> float:
    return round(len(wav) / SAMPLE_RATE, 2)
