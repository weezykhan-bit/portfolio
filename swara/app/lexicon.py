"""Pronunciation dictionary: word replacements applied before speech is generated.

Use it for brand names, acronyms and names the models mispronounce, e.g.
"Swara" -> "Swuh-raa", "OTT" -> "O T T", "Ltd" -> "Limited".
"""
from __future__ import annotations

import json
import re
import threading
import uuid

from .config import LEXICON_PATH

_lock = threading.Lock()


def load() -> list[dict]:
    try:
        data = json.loads(LEXICON_PATH.read_text(encoding="utf-8"))
        return [r for r in data if r.get("find")]
    except (FileNotFoundError, ValueError):
        return []


def save(rules: list[dict]) -> list[dict]:
    clean = []
    for r in rules[:500]:
        find = str(r.get("find", "")).strip()[:80]
        if not find:
            continue
        clean.append(
            {
                "id": r.get("id") or uuid.uuid4().hex[:8],
                "find": find,
                "say": str(r.get("say", "")).strip()[:160],
                "match_case": bool(r.get("match_case", False)),
            }
        )
    with _lock:
        tmp = LEXICON_PATH.with_suffix(".tmp")
        tmp.write_text(json.dumps(clean, ensure_ascii=False, indent=2), encoding="utf-8")
        tmp.replace(LEXICON_PATH)
    return clean


def apply(text: str, rules: list[dict] | None = None) -> str:
    rules = load() if rules is None else rules
    # Longest first so "Swara Studio" wins over "Swara".
    for r in sorted(rules, key=lambda r: -len(r["find"])):
        flags = 0 if r.get("match_case") else re.IGNORECASE
        # \b fails next to non-word characters (e.g. "C++"), so use lookarounds.
        pattern = rf"(?<!\w){re.escape(r['find'])}(?!\w)"
        text = re.sub(pattern, lambda _m, s=r["say"]: s, text, flags=flags)
    return text
