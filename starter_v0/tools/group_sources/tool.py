from __future__ import annotations

from typing import Any
from urllib.parse import urlsplit

from tools._shared import err


def _group_key(item: dict[str, Any], group_by: str) -> str:
    if group_by == "domain":
        url = item.get("url")
        if isinstance(url, str):
            try:
                parts = urlsplit(url)
                if parts.scheme in {"http", "https"} and parts.hostname:
                    return parts.hostname.lower().removeprefix("www.").rstrip(".")
            except ValueError:
                pass
        return "Unknown"
    value = item.get(group_by)
    return value.strip() if isinstance(value, str) and value.strip() else "Unknown"


def group_sources(items: list[dict[str, Any]] | None = None, group_by: str = "domain") -> dict[str, Any]:
    """Group collected research items by domain, source label, or section."""
    try:
        if not isinstance(items, list):
            raise TypeError("items must be a list of research item objects")
        if group_by not in {"domain", "source", "section"}:
            raise ValueError("group_by must be one of: domain, source, section")

        grouped: dict[str, list[dict[str, Any]]] = {}
        for index, item in enumerate(items):
            if not isinstance(item, dict):
                raise TypeError(f"items[{index}] must be an object")
            key = _group_key(item, group_by)
            grouped.setdefault(key, []).append(item)

        groups = [{"key": key, "item_count": len(group_items), "items": group_items} for key, group_items in grouped.items()]
        return {"tool": "group_sources", "group_by": group_by, "groups": groups, "group_count": len(groups), "item_count": len(items)}
    except Exception as exc:
        return err("group_sources", exc)
