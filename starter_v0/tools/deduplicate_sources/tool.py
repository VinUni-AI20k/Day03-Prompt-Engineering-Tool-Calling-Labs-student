from __future__ import annotations

from typing import Any
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from tools._shared import err


TRACKING_PARAMETERS = {"fbclid", "gclid", "dclid", "msclkid"}


def _source_key(url: Any) -> str:
    if not isinstance(url, str) or not url.strip():
        raise ValueError("Each item needs a non-empty string url")
    url = url.strip()
    if any(char.isspace() for char in url):
        raise ValueError("Source URLs must not contain whitespace")
    parsed = urlsplit(url)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise ValueError("Source URLs must be absolute HTTP or HTTPS URLs")
    if parsed.username is not None or parsed.password is not None:
        raise ValueError("Source URLs must not contain credentials")

    host = parsed.hostname.lower()
    if ":" in host:  # Preserve brackets around IPv6 addresses.
        host = f"[{host}]"
    port = parsed.port  # Also validates malformed or out-of-range ports.
    if port is not None and (parsed.scheme, port) not in {("http", 80), ("https", 443)}:
        host += f":{port}"
    query = [
        (key, value)
        for key, value in parse_qsl(parsed.query, keep_blank_values=True)
        if not key.lower().startswith("utm_") and key.lower() not in TRACKING_PARAMETERS
    ]
    # Preserve path case, meaningful query parameters/order, scheme and fragments.
    return urlunsplit((parsed.scheme, host, parsed.path or "/", urlencode(query), parsed.fragment))


def deduplicate_sources(items: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    """Keep the first item per normalized URL, without fetching or changing input."""
    try:
        if not isinstance(items, list):
            raise ValueError("items must be a list of source objects; use [] for no sources")
        seen: set[str] = set()
        unique: list[dict[str, Any]] = []
        for index, item in enumerate(items):
            if not isinstance(item, dict):
                raise ValueError(f"items[{index}] must be a source object")
            try:
                key = _source_key(item.get("url"))
            except ValueError as exc:
                raise ValueError(f"items[{index}]: {exc}") from exc
            if key not in seen:
                seen.add(key)
                unique.append(dict(item))
        return {
            "tool": "deduplicate_sources",
            "items": unique,
            "input_count": len(items),
            "item_count": len(unique),
            "duplicates_removed": len(items) - len(unique),
        }
    except Exception as exc:
        return err("deduplicate_sources", exc)
