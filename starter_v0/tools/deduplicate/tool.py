from __future__ import annotations

from typing import Any

from tools._shared import err


def deduplicate(items: list[dict[str, Any]], key_by: str = "url") -> dict[str, Any]:
    """Keep the first result for each normalized URL or title without changing inputs."""
    if not isinstance(items, list):
        return err("deduplicate", TypeError("items must be a list of result objects"))
    if not isinstance(key_by, str) or key_by not in ("url", "title"):
        return err("deduplicate", ValueError("key_by must be 'url' or 'title'"))

    seen: set[str] = set()
    unique_items: list[dict[str, Any]] = []
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            return err("deduplicate", TypeError(f"items[{index}] must be a result object"))

        value = item.get(key_by)
        if value is not None and not isinstance(value, str):
            return err("deduplicate", TypeError(f"items[{index}].{key_by} must be a string or null"))

        key = value.strip().casefold() if value is not None else ""
        if key_by == "url":
            key = key.rstrip("/")

        # Results without a usable key are distinct; do not silently drop them.
        if not key or key not in seen:
            unique_items.append(item)
            if key:
                seen.add(key)

    return {
        "tool": "deduplicate",
        "items": unique_items,
        "removed_count": len(items) - len(unique_items),
    }
