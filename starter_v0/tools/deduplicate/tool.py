from __future__ import annotations

from typing import Any
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from tools._shared import err


def canonical_url(url: str) -> str:
    parts = urlsplit(url.strip())
    if parts.scheme.lower() not in {"http", "https"} or not parts.hostname:
        raise ValueError("Each item needs an absolute HTTP(S) URL")
    if parts.username or parts.password:
        raise ValueError("URLs must not contain credentials")
    _ = parts.port  # validate malformed ports
    query = sorted((k, v) for k, v in parse_qsl(parts.query, keep_blank_values=True)
                   if not k.lower().startswith("utm_") and k.lower() not in {"fbclid", "gclid"})
    return urlunsplit((parts.scheme.lower(), parts.netloc.lower(), parts.path or "/", urlencode(query), ""))


def deduplicate_sources(items: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    """Keep the first item per normalized URL; never mutate input or fetch URLs."""
    try:
        if not isinstance(items, list) or len(items) > 100:
            raise ValueError("items must be a list of at most 100 objects")
        seen: set[str] = set()
        kept = []
        for item in items:
            if not isinstance(item, dict) or not isinstance(item.get("url"), str):
                raise ValueError("Each item must be an object with a string url")
            key = canonical_url(item["url"])
            if key not in seen:
                seen.add(key)
                kept.append(dict(item))
        return {"tool": "deduplicate", "items": kept, "input_count": len(items),
                "removed_count": len(items) - len(kept)}
    except Exception as exc:
        return err("deduplicate", exc)
