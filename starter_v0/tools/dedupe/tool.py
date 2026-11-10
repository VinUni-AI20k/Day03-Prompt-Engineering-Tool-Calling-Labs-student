from __future__ import annotations

from typing import Any
from urllib.parse import urlsplit

from tools._shared import err

ALLOWED_KEYS = {"url", "title"}


def _normalize(key: str, value: str) -> str:
    value = value.strip()
    if key == "url":
        parts = urlsplit(value)
        return f"{parts.scheme.lower()}://{parts.netloc.lower().removeprefix('www.')}{parts.path.rstrip('/')}?{parts.query}"
    return " ".join(value.lower().split())


def dedupe(items: list[dict[str, Any]] | None = None, key: str = "url") -> dict[str, Any]:
    """Remove duplicate items (keep the first one). Items without the key are kept as they are."""
    try:
        if key not in ALLOWED_KEYS:
            raise ValueError(f"key must be one of {sorted(ALLOWED_KEYS)}, got {key!r}")
        seen: set[str] = set()
        unique: list[dict[str, Any]] = []
        for item in items or []:
            raw = item.get(key) if isinstance(item, dict) else None
            if not isinstance(raw, str) or not raw.strip():
                unique.append(item)
                continue
            normalized = _normalize(key, raw)
            if normalized in seen:
                continue
            seen.add(normalized)
            unique.append(item)
        return {
            "tool": "dedupe",
            "items": unique,
            "item_count": len(unique),
            "removed_count": len(items or []) - len(unique),
        }
    except Exception as exc:
        return err("dedupe", exc)
