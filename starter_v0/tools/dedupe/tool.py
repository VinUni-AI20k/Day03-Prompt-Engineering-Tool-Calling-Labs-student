from __future__ import annotations

import re
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlparse

from tools._shared import fold_text


def _norm_url(url: str) -> str:
    parsed = urlparse(url.strip())
    host = parsed.netloc.lower().removeprefix("www.")
    path = parsed.path.rstrip("/")
    query = urlencode(sorted((k, v) for k, v in parse_qsl(parsed.query) if not k.lower().startswith("utm_")))
    return f"{host}{path}?{query}" if query else f"{host}{path}"


def _norm_title(title: str) -> str:
    return re.sub(r"\s+", " ", fold_text(title)).strip()


def dedupe_items(items: list[dict[str, Any]] | None = None, by: str = "url") -> dict[str, Any]:
    """Drop duplicate items, keeping the first occurrence. Items missing the key are kept."""
    by = by or "url"
    if by not in ("url", "title"):
        return {"tool": "dedupe", "error": "ValueError", "message": f"by must be 'url' or 'title', got {by!r}"}
    if items is None:
        items = []
    if not isinstance(items, list):
        return {"tool": "dedupe", "error": "TypeError", "message": "items must be a list of objects"}

    seen: set[str] = set()
    kept: list[Any] = []
    for item in items:
        raw = item.get(by) if isinstance(item, dict) else None
        key = (_norm_url(raw) if by == "url" else _norm_title(raw)) if isinstance(raw, str) and raw.strip() else ""
        if key and key in seen:
            continue
        if key:
            seen.add(key)
        kept.append(item)
    return {"tool": "dedupe", "by": by, "items": kept, "item_count": len(kept), "removed": len(items) - len(kept)}
