from __future__ import annotations

from typing import Any
from urllib.parse import urlsplit


def _valid_http_url(value: Any) -> bool:
    if not isinstance(value, str) or not value.strip() or any(char.isspace() for char in value):
        return False
    try:
        parsed = urlsplit(value.strip())
        return parsed.scheme.lower() in {"http", "https"} and bool(parsed.hostname)
    except ValueError:
        return False


def source_audit(items: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    """Check citation titles and HTTP(S) URLs without fetching or fact-checking them."""
    if not isinstance(items, list):
        return {
            "tool": "source_audit",
            "error": "TypeError",
            "message": "items must be a list of objects",
        }

    issues: list[dict[str, Any]] = []
    valid_count = 0

    for index, item in enumerate(items):
        problems: list[str] = []
        title: str | None = None

        if not isinstance(item, dict):
            problems.append("invalid_item")
        else:
            raw_title = item.get("title")
            if isinstance(raw_title, str) and raw_title.strip():
                title = raw_title.strip()
            else:
                problems.append("missing_title")

            if not item.get("url"):
                problems.append("missing_url")
            elif not _valid_http_url(item.get("url")):
                problems.append("invalid_url")

        if problems:
            issues.append({"index": index, "title": title, "problems": problems})
        else:
            valid_count += 1

    return {
        "tool": "source_audit",
        "checked_count": len(items),
        "valid_count": valid_count,
        "ok": not issues,
        "issues": issues,
    }
