from __future__ import annotations

import re
from collections import Counter
from typing import Any


STOP_WORDS = {
    "and", "are", "for", "from", "has", "have", "into", "its", "that", "the", "this", "to", "with",
    "các", "có", "của", "đã", "để", "đến", "được", "khi", "là", "một", "những", "trong", "và", "về",
}


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[^\W\d_]+", text.lower(), flags=re.UNICODE)


def extract_keywords(text: str = "", max_keywords: int = 5) -> dict[str, Any]:
    """Return the most frequent meaningful words from supplied text, offline."""
    try:
        if not isinstance(text, str):
            raise TypeError("text must be a string")
        if not text.strip():
            raise ValueError("text must not be empty")
        if isinstance(max_keywords, bool) or not isinstance(max_keywords, int):
            raise TypeError("max_keywords must be an integer")
        if not 1 <= max_keywords <= 20:
            raise ValueError("max_keywords must be between 1 and 20")

        tokens = [
            token for token in _tokenize(text)
            if (len(token) >= 3 or token == "ai") and token not in STOP_WORDS
        ]
        counts = Counter(tokens)
        first_seen = {token: index for index, token in enumerate(tokens)}
        ranked = sorted(counts, key=lambda token: (-counts[token], first_seen[token]))[:max_keywords]
        return {
            "tool": "extract_keywords",
            "keywords": [{"keyword": token, "count": counts[token]} for token in ranked],
            "text_length": len(text),
        }
    except Exception as exc:
        return {"tool": "extract_keywords", "error": type(exc).__name__, "message": str(exc)}
