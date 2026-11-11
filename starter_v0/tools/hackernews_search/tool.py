from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

import requests

from tools._shared import TIMEOUT, domain, err

BASE_URL = "https://hn.algolia.com/api/v1"
ALLOWED_TAGS = {"story", "show_hn", "ask_hn", "front_page", "comment"}
ALLOWED_SORT = {"relevance", "date"}


def _to_timestamp(value: str, *, end_of_day: bool = False) -> int:
    """'YYYY-MM-DD' -> unix seconds (UTC). Raises ValueError on a bad format."""
    day = datetime.strptime(value.strip(), "%Y-%m-%d").replace(tzinfo=timezone.utc)
    if end_of_day:
        day = day + timedelta(days=1) - timedelta(seconds=1)
    return int(day.timestamp())


def _hit_item(hit: dict[str, Any]) -> dict[str, Any]:
    object_id = hit.get("objectID") or hit.get("story_id")
    hn_url = f"https://news.ycombinator.com/item?id={object_id}" if object_id else ""
    url = hit.get("url") or hn_url
    title = hit.get("title") or hit.get("story_title") or ""
    return {
        "title": title,
        "url": url,
        "source": domain(url) if hit.get("url") else "news.ycombinator.com",
        "hn_url": hn_url,
        "points": hit.get("points") or 0,
        "author": hit.get("author") or "",
        "num_comments": hit.get("num_comments") or 0,
        "created_at": hit.get("created_at") or "",
        "summary": f"{hit.get('points') or 0} points · {hit.get('num_comments') or 0} comments · by {hit.get('author') or '?'}",
    }


def hackernews_search(
    query: str = "",
    tags: str = "story",
    sort: str = "relevance",
    date_from: str = "",
    date_to: str = "",
    limit: int = 5,
) -> dict[str, Any]:
    """Search Hacker News via the public Algolia API (no key required)."""
    try:
        query = (query or "").strip()
        tags = tags if tags in ALLOWED_TAGS else "story"
        sort = sort if sort in ALLOWED_SORT else "relevance"
        if not query and tags != "front_page":
            raise ValueError("query is required (or use tags='front_page' to list the current front page)")
        try:
            hits_per_page = max(1, min(int(limit or 5), 20))
        except (TypeError, ValueError):
            hits_per_page = 5

        numeric_filters = []
        if date_from:
            numeric_filters.append(f"created_at_i>={_to_timestamp(date_from)}")
        if date_to:
            numeric_filters.append(f"created_at_i<={_to_timestamp(date_to, end_of_day=True)}")

        params: dict[str, Any] = {"query": query, "tags": tags, "hitsPerPage": hits_per_page}
        if numeric_filters:
            params["numericFilters"] = ",".join(numeric_filters)

        endpoint = "search_by_date" if sort == "date" else "search"
        response = requests.get(f"{BASE_URL}/{endpoint}", params=params, timeout=TIMEOUT)
        response.raise_for_status()
        hits = response.json().get("hits", [])
        items = [_hit_item(hit) for hit in hits[:hits_per_page]]
        return {
            "tool": "hackernews_search",
            "query": query,
            "tags": tags,
            "sort": sort,
            "date_from": date_from or None,
            "date_to": date_to or None,
            "items": items,
        }
    except Exception as exc:
        return err("hackernews_search", exc)
