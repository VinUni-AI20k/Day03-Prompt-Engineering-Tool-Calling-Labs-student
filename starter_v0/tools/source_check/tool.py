from __future__ import annotations

import ipaddress
import re
from typing import Any
from urllib.parse import urlsplit

from tools._shared import err


def _valid_url(value: Any) -> bool:
    """Check URL syntax only; never fetch URLs or resolve hostnames."""
    if not isinstance(value, str) or not value or any(ch.isspace() or ord(ch) < 32 for ch in value):
        return False
    if "\\" in value:
        return False
    try:
        parsed = urlsplit(value)
        if parsed.scheme.lower() not in {"http", "https"} or not parsed.hostname:
            return False
        if parsed.username is not None or parsed.password is not None:
            return False
        # Accessing port validates malformed/out-of-range ports.
        if parsed.port is not None and parsed.port == 0:
            return False
        host = parsed.hostname
        try:
            ipaddress.ip_address(host)
            return True
        except ValueError:
            pass
        ascii_host = host.encode("idna").decode("ascii").rstrip(".")
        return len(ascii_host) <= 253 and all(
            re.fullmatch(r"[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?", label)
            for label in ascii_host.split(".")
        )
    except (ValueError, UnicodeError):
        return False


def check_sources(items: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    """Validate citation metadata, retaining input order and leaving input untouched."""
    try:
        if not isinstance(items, list):
            raise ValueError("items must be a list of research items")
        results: list[dict[str, Any]] = []
        valid_items: list[dict[str, Any]] = []
        for index, item in enumerate(items):
            issues: list[str] = []
            if not isinstance(item, dict):
                issues.append("invalid_item")
            else:
                url = item.get("url")
                if url is None or (isinstance(url, str) and not url.strip()):
                    issues.append("missing_url")
                elif not _valid_url(url):
                    issues.append("invalid_url")
                source = item.get("source")
                if source is None or (isinstance(source, str) and not source.strip()):
                    issues.append("missing_source")
                elif not isinstance(source, str):
                    issues.append("invalid_source")
            results.append({"index": index, "valid": not issues, "issues": issues})
            if not issues:
                valid_items.append(dict(item))
        return {
            "tool": "source_check",
            "item_count": len(items),
            "valid_count": len(valid_items),
            "invalid_count": len(items) - len(valid_items),
            "all_valid": bool(items) and len(valid_items) == len(items),
            "results": results,
            "items": valid_items,
            "validation_scope": "citation_metadata_only",
        }
    except Exception as exc:
        return err("source_check", exc)
