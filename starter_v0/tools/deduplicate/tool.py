from __future__ import annotations

from copy import deepcopy
from typing import Any
from urllib.parse import urldefrag, urlsplit


def deduplicate_items(items: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    """Keep the first item per HTTP(S) URL, ignoring fragments only."""
    try:
        if not isinstance(items, list):
            raise ValueError("items must be a list")
        seen: set[str] = set()
        unique: list[dict[str, Any]] = []
        for index, item in enumerate(items):
            if not isinstance(item, dict):
                raise ValueError(f"items[{index}] must be an object")
            url = item.get("url")
            if not isinstance(url, str) or not url or any(c.isspace() for c in url):
                raise ValueError(f"items[{index}].url must be a valid HTTP(S) URL")
            parsed = urlsplit(url)
            if parsed.scheme not in ("http", "https") or not parsed.hostname:
                raise ValueError(f"items[{index}].url must be a valid HTTP(S) URL")
            # Accessing port also validates malformed or out-of-range ports.
            _ = parsed.port
            key = urldefrag(url)[0]
            if key not in seen:
                seen.add(key)
                unique.append(deepcopy(item))
        return {"tool": "deduplicate", "items": unique, "removed_count": len(items) - len(unique)}
    except ValueError as exc:
        return {"tool": "deduplicate", "error": "invalid_input", "message": str(exc)}
