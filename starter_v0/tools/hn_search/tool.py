from __future__ import annotations

import time
from typing import Any

import requests

from tools._shared import TIMEOUT, domain, err

HN_SEARCH_URL = "https://hn.algolia.com/api/v1/search"
HN_SEARCH_BY_DATE_URL = "https://hn.algolia.com/api/v1/search_by_date"
TIMEFRAME_SECONDS = {"day": 86_400, "week": 7 * 86_400, "month": 30 * 86_400, "year": 365 * 86_400}


def hn_search(query: str = "", sort_by: str = "relevance", timeframe: str | None = None, limit: int = 5) -> dict[str, Any]:
    """Tìm thảo luận trên Hacker News (Algolia API, không cần key)."""
    try:
        query = " ".join(str(query or "").split())
        if not query:
            return {"tool": "hn_search", "error": "ValueError", "message": "query must not be empty", "items": []}
        try:
            limit = max(1, min(int(5 if limit is None else limit), 20))  # model hay gửi "5", 0, -1
        except (TypeError, ValueError):
            limit = 5
        sort_by = sort_by if sort_by in {"relevance", "date"} else "relevance"
        url = HN_SEARCH_BY_DATE_URL if sort_by == "date" else HN_SEARCH_URL

        params: dict[str, Any] = {"query": query, "tags": "story", "hitsPerPage": limit}
        if timeframe in TIMEFRAME_SECONDS:
            params["numericFilters"] = f"created_at_i>{int(time.time()) - TIMEFRAME_SECONDS[timeframe]}"

        response = requests.get(url, params=params, timeout=TIMEOUT)
        response.raise_for_status()
        items = []
        for hit in response.json().get("hits", [])[:limit]:
            object_id = hit.get("objectID")
            if not object_id:
                continue
            discussion_url = f"https://news.ycombinator.com/item?id={object_id}"
            link = hit.get("url") or discussion_url
            items.append({
                "title": hit.get("title") or "",
                "url": link,
                "discussion_url": discussion_url,
                "source": domain(link) or "news.ycombinator.com",
                "date": hit.get("created_at"),
                "summary": f"{hit.get('points') or 0} points, {hit.get('num_comments') or 0} comments on Hacker News",
                "metrics": {"points": hit.get("points"), "comments": hit.get("num_comments")},
            })
        return {"tool": "hn_search", "query": query, "sort_by": sort_by, "timeframe": timeframe, "items": items}
    except Exception as exc:
        return err("hn_search", exc)
