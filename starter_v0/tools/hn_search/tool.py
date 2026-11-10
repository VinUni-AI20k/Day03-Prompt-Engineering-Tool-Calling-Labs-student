from __future__ import annotations

import html
import re
import time
from typing import Any

import requests

from tools._shared import TIMEOUT, domain, err


API_BASE = "https://hn.algolia.com/api/v1"
SORT_ENDPOINTS = {"relevance": "search", "date": "search_by_date"}
TIMEFRAME_SECONDS = {"day": 86_400, "week": 7 * 86_400, "month": 30 * 86_400, "year": 365 * 86_400}
MAX_LIMIT = 20


def _clean_limit(limit: Any) -> int:
    """Accept ints and numeric strings from the model ("5"); clamp to 1..MAX_LIMIT."""
    if isinstance(limit, bool):
        raise ValueError(f"limit must be an integer, got {limit!r}")
    if limit is None or limit == "":
        return 5
    try:
        value = int(str(limit).strip())
    except ValueError as exc:
        raise ValueError(f"limit must be an integer, got {limit!r}") from exc
    return max(1, min(MAX_LIMIT, value))


def _plain_text(raw: Any) -> str:
    """story_text from Algolia is HTML (<p>, <a>, &#x2F;) -> plain text, max 500 chars."""
    text = re.sub(r"<[^>]+>", " ", str(raw or ""))
    text = " ".join(html.unescape(text).split())
    return text[:500]


def _hit_item(hit: dict[str, Any]) -> dict[str, Any]:
    object_id = str(hit.get("objectID") or "")
    discussion = f"https://news.ycombinator.com/item?id={object_id}" if object_id else ""
    url = hit.get("url") or discussion
    return {
        "title": hit.get("title") or hit.get("story_title") or "",
        "url": url,
        "source": domain(url) if hit.get("url") else "news.ycombinator.com",
        "summary": _plain_text(hit.get("story_text")),
        "date": hit.get("created_at"),
        "discussion_url": discussion,
        "metrics": {"points": hit.get("points"), "comments": hit.get("num_comments")},
    }


def hn_search(query: str = "", sort_by: str = "relevance", timeframe: str = "any", limit: int = 5) -> dict[str, Any]:
    """Search Hacker News stories via the free Algolia HN API (no API key needed)."""
    try:
        if not isinstance(query, str) or not query.strip():
            raise ValueError("query must be a non-empty string")
        sort_by = (sort_by or "relevance").strip().lower()
        if sort_by not in SORT_ENDPOINTS:
            raise ValueError(f"sort_by must be one of {sorted(SORT_ENDPOINTS)}, got {sort_by!r}")
        timeframe = (timeframe or "any").strip().lower()
        if timeframe != "any" and timeframe not in TIMEFRAME_SECONDS:
            raise ValueError(f"timeframe must be one of ['any', 'day', 'week', 'month', 'year'], got {timeframe!r}")
        hits_per_page = _clean_limit(limit)

        params: dict[str, Any] = {"query": query.strip(), "tags": "story", "hitsPerPage": hits_per_page}
        if timeframe != "any":
            since = int(time.time()) - TIMEFRAME_SECONDS[timeframe]
            params["numericFilters"] = f"created_at_i>{since}"

        response = requests.get(f"{API_BASE}/{SORT_ENDPOINTS[sort_by]}", params=params, timeout=TIMEOUT)
        response.raise_for_status()
        hits = response.json().get("hits") or []
        items = [_hit_item(hit) for hit in hits if isinstance(hit, dict)][:hits_per_page]
        return {
            "tool": "hn_search",
            "query": query.strip(),
            "sort_by": sort_by,
            "timeframe": timeframe,
            "items": items,
        }
    except Exception as exc:
        return err("hn_search", exc)
