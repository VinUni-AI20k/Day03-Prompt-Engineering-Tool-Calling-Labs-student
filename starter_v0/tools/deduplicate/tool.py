from __future__ import annotations

from typing import Any
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit


def deduplicate_sources(items: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    """Keep the first item per URL, ignoring fragments and tracking parameters."""
    try:
        if not isinstance(items, list):
            raise ValueError("items must be a list of objects with HTTP(S) URLs")
        kept: list[dict[str, Any]] = []
        seen: set[str] = set()
        for item in items:
            if not isinstance(item, dict) or not isinstance(item.get("url"), str):
                raise ValueError("each item must contain a string url")
            parts = urlsplit(item["url"].strip())
            if parts.scheme.lower() not in {"http", "https"} or not parts.hostname or parts.username or parts.password:
                raise ValueError("each url must be an absolute HTTP(S) URL without credentials")
            query = [(k, v) for k, v in parse_qsl(parts.query, keep_blank_values=True)
                     if not k.lower().startswith("utm_") and k.lower() not in {"fbclid", "gclid"}]
            canonical = urlunsplit((parts.scheme.lower(), parts.netloc.lower(), parts.path or "/",
                                   urlencode(sorted(query)), ""))
            if canonical not in seen:
                seen.add(canonical)
                kept.append(dict(item))
        return {"tool": "deduplicate", "items": kept, "item_count": len(kept),
                "duplicate_count": len(items) - len(kept)}
    except Exception as exc:
        return {"tool": "deduplicate", "error": type(exc).__name__, "message": str(exc)}
