from __future__ import annotations

from typing import Any

import requests

from tools._shared import TIMEOUT, err

SORTS = {"relevance": "search", "date": "search_by_date"}


def search_hackernews(query: str = "", sort: str = "relevance", limit: int = 5) -> dict[str, Any]:
    try:
        if not isinstance(query, str) or not query.strip():
            raise ValueError("query must be a non-empty string")
        if sort not in SORTS:
            raise ValueError(f"sort must be one of {sorted(SORTS)}")
        count = int(limit or 5)
        if count < 1:
            count = 5
        count = min(count, 20)

        response = requests.get(
            f"https://hn.algolia.com/api/v1/{SORTS[sort]}",
            params={"query": query.strip(), "tags": "story", "hitsPerPage": count},
            timeout=TIMEOUT,
        )
        response.raise_for_status()
        data = response.json()
        if not isinstance(data, dict):
            raise ValueError("Hacker News response must be a JSON object")

        items = []
        for hit in data.get("hits") or []:
            object_id = hit.get("objectID")
            if not object_id or not hit.get("title"):
                continue
            discussion = f"https://news.ycombinator.com/item?id={object_id}"
            items.append({
                "title": hit["title"],
                "url": hit.get("url") or discussion,
                "source": "news.ycombinator.com",
                "summary": f"{hit.get('points') or 0} points, {hit.get('num_comments') or 0} comments",
                "discussion_url": discussion,
                "date": hit.get("created_at"),
            })
        return {"tool": "hackernews", "query": query.strip(), "sort": sort, "items": items[:count]}
    except Exception as exc:
        return err("hackernews", exc)
