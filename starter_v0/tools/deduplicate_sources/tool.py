from __future__ import annotations

from typing import Any


def deduplicate_sources(
    items: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    if not isinstance(items, list):
        return {
            "error": "TypeError",
            "message": "items must be a list",
        }

    filtered: list[dict[str, Any]] = []
    seen_urls: set[str] = set()
    removed_count = 0

    for index, item in enumerate(items):
        if not isinstance(item, dict):
            return {
                "error": "TypeError",
                "message": f"items[{index}] must be an object",
            }

        url = item.get("url")

        # Item không có URL được giữ nguyên và không dùng để deduplicate.
        if url is None or url == "":
            filtered.append(item)
            continue

        if not isinstance(url, str):
            return {
                "error": "TypeError",
                "message": f"items[{index}].url must be a string",
            }

        if url in seen_urls:
            removed_count += 1
            continue

        seen_urls.add(url)
        filtered.append(item)

    return {
        "tool": "deduplicate_sources",
        "items": filtered,
        "removed_count": removed_count,
    }