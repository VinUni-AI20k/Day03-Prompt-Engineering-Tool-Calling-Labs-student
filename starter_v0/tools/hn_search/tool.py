from __future__ import annotations
from typing import Any
import requests
from tools._shared import TIMEOUT, err

def hn_search(query: str = "", sort: str = "relevance", limit: int = 5) -> dict[str, Any]:
    try:
        if not str(query).strip():
            raise ValueError("query is empty")
        limit = max(1, min(int(limit or 5), 20))
        endpoint = "search_by_date" if sort == "latest" else "search"
        r = requests.get(f"https://hn.algolia.com/api/v1/{endpoint}",
                         params={"query": query, "tags": "story", "hitsPerPage": limit}, timeout=TIMEOUT)
        r.raise_for_status()
        items = [{
            "title": h.get("title"),
            "url": h.get("url") or f"https://news.ycombinator.com/item?id={h.get('objectID')}",
            "source": "news.ycombinator.com",
            "summary": f"{h.get('points', 0)} points · {h.get('num_comments', 0)} comments",
        } for h in r.json().get("hits", [])][:limit]
        return {"tool": "hn_search", "query": query, "sort": sort, "items": items}
    except Exception as exc:
        return err("hn_search", exc)