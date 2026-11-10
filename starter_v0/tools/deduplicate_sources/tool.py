from __future__ import annotations

from typing import Any
from urllib.parse import urlsplit, urlunsplit


def _canonical_url(url: str) -> str:
    parsed = urlsplit(url.strip())
    if not parsed.scheme or not parsed.netloc:
        return url.strip()

    hostname = (parsed.hostname or "").lower()
    port = parsed.port
    netloc = hostname
    if port is not None and not (
        (parsed.scheme.lower() == "http" and port == 80)
        or (parsed.scheme.lower() == "https" and port == 443)
    ):
        netloc = f"{hostname}:{port}"

    path = parsed.path.rstrip("/") or "/"
    return urlunsplit((parsed.scheme.lower(), netloc, path, parsed.query, parsed.fragment))


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

        canonical_url = _canonical_url(url)
        if canonical_url in seen_urls:
            removed_count += 1
            continue

        seen_urls.add(canonical_url)
        filtered.append(item)

    return {
        "tool": "deduplicate_sources",
        "items": filtered,
        "removed_count": removed_count,
    }