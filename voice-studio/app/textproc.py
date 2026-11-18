"""Text clean-up and chunking.

Cloning models drift or cut off when given long passages in one go, so long
text is split at sentence boundaries into chunks the model handles well, then
the audio is stitched back together.
"""
from __future__ import annotations

import re

# Sentence enders for Latin scripts plus Hindi danda (।) and CJK full stops.
_SENTENCE_RE = re.compile(r"(?<=[.!?।。！？])[\"'”’)\]]*\s+")
_CLAUSE_RE = re.compile(r"(?<=[,;:—–])\s+")
_WS_RE = re.compile(r"[ \t]+")


def normalize(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = text.replace(" ", " ")
    text = _WS_RE.sub(" ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _split_long(sentence: str, max_chars: int) -> list[str]:
    """Split one over-long sentence at commas, then at word boundaries."""
    if len(sentence) <= max_chars:
        return [sentence]
    parts: list[str] = []
    buf = ""
    for clause in _CLAUSE_RE.split(sentence):
        if len(clause) > max_chars:
            words = clause.split(" ")
            for w in words:
                if buf and len(buf) + 1 + len(w) > max_chars:
                    parts.append(buf)
                    buf = w
                else:
                    buf = f"{buf} {w}".strip()
            continue
        if buf and len(buf) + 1 + len(clause) > max_chars:
            parts.append(buf)
            buf = clause
        else:
            buf = f"{buf} {clause}".strip()
    if buf:
        parts.append(buf)
    return parts


def chunk_text(text: str, max_chars: int = 280) -> list[str]:
    """Return speakable chunks of at most ``max_chars`` characters."""
    return [c for c, _ in chunk_with_pauses(text, max_chars)]


def chunk_with_pauses(
    text: str, max_chars: int = 280, sentence_pause: float = 0.2, paragraph_pause: float = 0.55
) -> list[tuple[str, float]]:
    """Return ``(chunk, pause_after_seconds)`` pairs.

    Paragraph breaks are always chunk boundaries and get a longer pause, so the
    stitched audio keeps the rhythm of the original text.
    """
    out: list[tuple[str, float]] = []
    for para in _paragraphs(text):
        chunks = _chunk_paragraph(para, max_chars)
        for i, c in enumerate(chunks):
            out.append((c, paragraph_pause if i == len(chunks) - 1 else sentence_pause))
    return out


def _paragraphs(text: str) -> list[str]:
    text = normalize(text)
    return [p.strip() for p in text.split("\n") if p.strip()]


def _chunk_paragraph(para: str, max_chars: int) -> list[str]:
    chunks: list[str] = []
    buf = ""
    for sentence in _SENTENCE_RE.split(para):
        sentence = sentence.strip()
        if not sentence:
            continue
        for piece in _split_long(sentence, max_chars):
            if buf and len(buf) + 1 + len(piece) > max_chars:
                chunks.append(buf)
                buf = piece
            else:
                buf = f"{buf} {piece}".strip()
    if buf:
        chunks.append(buf)
    return chunks
