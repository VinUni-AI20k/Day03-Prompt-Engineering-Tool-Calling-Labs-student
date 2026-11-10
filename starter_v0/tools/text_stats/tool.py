from __future__ import annotations

import math
import re
from typing import Any

from tools._shared import err

WORDS_PER_MINUTE = 200


def text_stats(text: str = "") -> dict[str, Any]:
    """Count characters, words, sentences and estimate reading time for a piece of text."""
    try:
        if text is None:
            text = ""
        if not isinstance(text, str):
            raise TypeError(f"text must be a string, got {type(text).__name__}")
        words = re.findall(r"\S+", text)
        sentences = [part for part in re.split(r"[.!?…]+", text) if part.strip()]
        return {
            "tool": "text_stats",
            "chars": len(text),
            "words": len(words),
            "sentences": len(sentences),
            "reading_minutes": math.ceil(len(words) / WORDS_PER_MINUTE) if words else 0,
        }
    except Exception as exc:
        return err("text_stats", exc)
