from __future__ import annotations

import re
from typing import Any


def _words(text: str) -> set[str]:
    return set(re.findall(r"\w+", text.casefold()))


def rank_sources(
    items: list[dict[str, Any]],
    query: str,
    limit: int = 5,
) -> dict[str, Any]:
    """Rank sources by keyword overlap, not by truth or reliability."""
    if not isinstance(items, list) or not all(isinstance(item, dict) for item in items):
        return {"error": "invalid_input", "message": "items must be a list of objects"}
    if not isinstance(query, str) or not query.strip():
        return {"error": "invalid_input", "message": "query must be a non-empty string"}
    if isinstance(limit, bool) or not isinstance(limit, int) or limit < 1:
        return {"error": "invalid_input", "message": "limit must be a positive integer"}

    query_words = _words(query)

    def score(item: dict[str, Any]) -> int:
        title = item.get("title") or ""
        summary = item.get("summary") or ""
        text = f"{title} {summary}"
        if not isinstance(title, str) or not isinstance(summary, str):
            return 0
        return len(query_words & _words(text))

    ranked = sorted(items, key=score, reverse=True)
    return {"items": ranked[:limit], "ranked_count": len(ranked)}