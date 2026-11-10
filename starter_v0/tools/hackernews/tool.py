from __future__ import annotations

from typing import Any

import requests

from tools._shared import TIMEOUT, domain, err


def search_hackernews(query: str = "", sort_by: str = "relevance", limit: int = 5) -> dict[str, Any]:
    """Search Hacker News stories via Algolia HN API."""
    try:
        clean_query = query.strip() if isinstance(query, str) else str(query or "").strip()
        if not clean_query:
            raise ValueError("Missing query for hackernews search")

        sort_mode = sort_by if sort_by in {"relevance", "date"} else "relevance"
        try:
            count = int(limit) if limit is not None else 5
        except (TypeError, ValueError):
            count = 5
        count = max(1, min(count if count > 0 else 5, 20))

        endpoint = (
            "https://hn.algolia.com/api/v1/search_by_date"
            if sort_mode == "date"
            else "https://hn.algolia.com/api/v1/search"
        )
        response = requests.get(
            endpoint,
            params={"query": clean_query, "tags": "story", "hitsPerPage": count},
            timeout=TIMEOUT,
        )
        response.raise_for_status()
        data = response.json()

        items: list[dict[str, Any]] = []
        for hit in (data.get("hits") or [])[:count]:
            object_id = str(hit.get("objectID") or "").strip()
            hn_url = f"https://news.ycombinator.com/item?id={object_id}" if object_id else ""
            url = (hit.get("url") or "").strip() or hn_url
            title = hit.get("title") or hit.get("story_title") or "(untitled)"
            author = hit.get("author") or "unknown"
            points = hit.get("points") or 0
            comments = hit.get("num_comments") or 0
            items.append({
                "title": title,
                "url": url,
                "source": domain(url) or "news.ycombinator.com",
                "summary": f"HN by {author} ({points} points, {comments} comments)",
                "hn_url": hn_url,
                "points": points,
                "num_comments": comments,
            })

        return {
            "tool": "hackernews",
            "query": clean_query,
            "sort_by": sort_mode,
            "items": items,
        }
    except Exception as exc:
        return err("hackernews", exc)

