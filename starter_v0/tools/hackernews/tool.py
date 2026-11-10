from __future__ import annotations

from typing import Any

import requests

from tools._limits import clamp_int, pick
from tools._shared import TIMEOUT, domain, err

HN_API = "https://hn.algolia.com/api/v1"


def search_hackernews(query: str = "", sort: str = "relevance", limit: int = 5) -> dict[str, Any]:
    """Search Hacker News stories via the public Algolia API (no key)."""
    try:
        query = (query or "").strip()
        if not query:
            raise ValueError("query must not be empty")
        sort = pick(sort, ("relevance", "date"), "relevance")
        limit = clamp_int(limit, 5)
        endpoint = "search_by_date" if sort == "date" else "search"
        response = requests.get(
            f"{HN_API}/{endpoint}",
            params={"query": query, "tags": "story", "hitsPerPage": limit},
            timeout=TIMEOUT,
        )
        response.raise_for_status()
        items = []
        for hit in response.json().get("hits", [])[:limit]:
            story_id = hit.get("objectID") or ""
            discussion = f"https://news.ycombinator.com/item?id={story_id}" if story_id else ""
            url = hit.get("url") or discussion
            items.append({
                "title": hit.get("title") or "",
                "url": url,
                "source": domain(url) or "news.ycombinator.com",
                "summary": f"{hit.get('points') or 0} points, {hit.get('num_comments') or 0} comments",
                "discussion_url": discussion,
                "date": hit.get("created_at"),
            })
        return {"tool": "search_hackernews", "query": query, "sort": sort, "items": items}
    except Exception as exc:
        return err("search_hackernews", exc)
