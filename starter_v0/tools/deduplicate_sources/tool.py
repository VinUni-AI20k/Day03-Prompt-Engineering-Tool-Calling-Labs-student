from __future__ import annotations

from typing import Any
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from tools._shared import err, fold_text


ALLOWED_STRATEGIES = {"url", "title", "url_or_title"}


def _canonical_url(value: str) -> str:
    parts = urlsplit(value.strip())
    query = urlencode([
        (key, item) for key, item in parse_qsl(parts.query, keep_blank_values=True)
        if not key.lower().startswith("utm_")
    ])
    path = parts.path.rstrip("/") or "/"
    return urlunsplit((parts.scheme.lower(), parts.netloc.lower(), path, query, ""))


def _canonical_title(value: str, case_sensitive: bool) -> str:
    compact = " ".join(value.split())
    return compact if case_sensitive else fold_text(compact)


def deduplicate_sources(
    items: list[dict[str, Any]] | None = None,
    strategy: str = "url_or_title",
    case_sensitive: bool = False,
) -> dict[str, Any]:
    """Remove duplicate research sources while preserving their original order."""
    try:
        if not isinstance(items, list):
            raise ValueError("items must be a list of source objects")
        if strategy not in ALLOWED_STRATEGIES:
            raise ValueError(f"strategy must be one of: {', '.join(sorted(ALLOWED_STRATEGIES))}")
        if not isinstance(case_sensitive, bool):
            raise ValueError("case_sensitive must be a boolean")

        unique_items: list[dict[str, Any]] = []
        duplicates: list[dict[str, Any]] = []
        seen_urls: dict[str, int] = {}
        seen_titles: dict[str, int] = {}

        for index, item in enumerate(items):
            if not isinstance(item, dict):
                raise ValueError(f"items[{index}] must be an object")
            raw_url = item.get("url", "")
            raw_title = item.get("title", "")
            if not isinstance(raw_url, str) or not isinstance(raw_title, str):
                raise ValueError(f"items[{index}].url and title must be strings when present")

            url_key = _canonical_url(raw_url) if raw_url.strip() else ""
            title_key = _canonical_title(raw_title, case_sensitive) if raw_title.strip() else ""
            duplicate_of: int | None = None
            reason = ""
            if strategy in {"url", "url_or_title"} and url_key and url_key in seen_urls:
                duplicate_of, reason = seen_urls[url_key], "url"
            elif strategy in {"title", "url_or_title"} and title_key and title_key in seen_titles:
                duplicate_of, reason = seen_titles[title_key], "title"

            if duplicate_of is not None:
                duplicates.append({
                    "duplicate_index": index,
                    "kept_index": duplicate_of,
                    "reason": reason,
                    "item": item,
                })
                continue

            unique_items.append(item)
            if url_key:
                seen_urls[url_key] = index
            if title_key:
                seen_titles[title_key] = index

        return {
            "tool": "deduplicate_sources",
            "strategy": strategy,
            "input_count": len(items),
            "unique_count": len(unique_items),
            "duplicate_count": len(duplicates),
            "items": unique_items,
            "duplicates": duplicates,
        }
    except Exception as exc:
        return err("deduplicate_sources", exc)
