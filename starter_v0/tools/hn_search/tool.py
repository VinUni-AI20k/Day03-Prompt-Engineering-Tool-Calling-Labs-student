from __future__ import annotations

from typing import Any

import requests

from tools._shared import TIMEOUT, err

API_URL = "https://hn.algolia.com/api/v1/search"
API_URL_BY_DATE = "https://hn.algolia.com/api/v1/search_by_date"
MAX_LIMIT = 20


def _to_limit(value: Any, default: int = 5) -> int:
    try:
        number = int(value)
    except (TypeError, ValueError):
        return default
    return max(1, min(number, MAX_LIMIT))


def hn_search(query: str = "", sort: str = "relevance", limit: int = 5) -> dict[str, Any]:
    """Search Hacker News stories via the public Algolia API (no key needed)."""
    if not isinstance(query, str) or not query.strip():
        return {"tool": "hn_search", "error": "invalid_query", "message": "query must be a non-empty string"}
    if sort not in {"relevance", "date"}:
        sort = "relevance"
    limit = _to_limit(limit)

    try:
        response = requests.get(
            API_URL_BY_DATE if sort == "date" else API_URL,
            params={"query": query.strip(), "tags": "story", "hitsPerPage": limit},
            timeout=TIMEOUT,
        )
        response.raise_for_status()
        hits = response.json().get("hits", [])
    except Exception as exc:  # return an error dict instead of raising
        return err("hn_search", exc)

    items = []
    for hit in hits[:limit]:
        story_id = hit.get("objectID") or ""
        discussion_url = f"https://news.ycombinator.com/item?id={story_id}" if story_id else ""
        items.append({
            "title": hit.get("title") or "",
            "url": hit.get("url") or discussion_url,
            "discussion_url": discussion_url,
            "source": "news.ycombinator.com",
            "points": hit.get("points") or 0,
            "num_comments": hit.get("num_comments") or 0,
            "published_at": hit.get("created_at") or "",
        })
    return {"tool": "hn_search", "query": query.strip(), "sort": sort, "items": items}
