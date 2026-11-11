from __future__ import annotations

import re
from typing import Any
from urllib.parse import unquote_plus, urlsplit, urlunsplit

from tools._shared import err


_TRACKING_PARAMS = {"fbclid", "gclid", "dclid", "msclkid", "mc_cid", "mc_eid"}


def _normalize_url(url: Any) -> str:
    if not isinstance(url, str) or not url:
        raise ValueError("url must be a non-empty absolute HTTP(S) URL")
    if any(char.isspace() or ord(char) < 32 or ord(char) == 127 for char in url):
        raise ValueError("url must not contain whitespace or control characters")
    if "\\" in url or re.search(r"%(?![0-9a-fA-F]{2})", url):
        raise ValueError("url contains a backslash or an invalid percent escape")

    parts = urlsplit(url)
    hostname = parts.hostname
    if parts.scheme not in {"http", "https"} or not hostname:
        raise ValueError("url must be an absolute HTTP(S) URL with a hostname")
    # urlsplit is permissive; accessing port also validates its type and range.
    _ = parts.port
    if ":" not in hostname:  # IPv6 literals are validated by urlsplit.
        ascii_host = hostname.removesuffix(".").encode("idna").decode("ascii")
        if len(ascii_host) > 253 or any(
            not re.fullmatch(r"[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?", label)
            for label in ascii_host.split(".")
        ):
            raise ValueError("url has an invalid hostname")

    # Preserve meaningful query fields verbatim, including order, repeated keys,
    # blank values and percent encoding. Decode only the key to detect tracking.
    query_fields = []
    for field in parts.query.split("&"):
        key = unquote_plus(field.partition("=")[0]).lower()
        if not key.startswith("utm_") and key not in _TRACKING_PARAMS:
            query_fields.append(field)
    userinfo, separator, host_port = parts.netloc.rpartition("@")
    netloc = userinfo + separator + host_port.lower()
    return urlunsplit((parts.scheme, netloc, parts.path, "&".join(query_fields), ""))


def dedupe_sources(items: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    """Remove duplicate URLs from existing items, keeping the first item intact."""
    try:
        if not isinstance(items, list):
            raise TypeError("items must be a list of research item objects")
        seen: set[str] = set()
        unique: list[dict[str, Any]] = []
        for index, item in enumerate(items):
            if not isinstance(item, dict):
                raise TypeError(f"items[{index}] must be an object with a url")
            try:
                normalized_url = _normalize_url(item.get("url"))
            except ValueError as exc:
                raise ValueError(f"items[{index}].url is invalid: {exc}") from exc
            if normalized_url not in seen:
                seen.add(normalized_url)
                unique.append(item)
        return {"tool": "dedupe_sources", "items": unique, "duplicate_count": len(items) - len(unique)}
    except Exception as exc:
        return err("dedupe_sources", exc)
