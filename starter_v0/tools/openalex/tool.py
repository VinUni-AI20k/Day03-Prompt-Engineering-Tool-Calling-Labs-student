from __future__ import annotations

from datetime import date
from typing import Any

import requests

from tools._limits import clamp_int, pick
from tools._shared import TIMEOUT, err

OPENALEX = "https://api.openalex.org"
USER_AGENT = "AI20k-Day03-Research-Agent/1.0 (educational lab)"
SORTS = {"cited": "cited_by_count:desc", "recent": "publication_date:desc"}


def _clean(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def search_openalex(query: str = "", author: str = "", sort: str = "cited", limit: int = 5) -> dict[str, Any]:
    """Search scholarly works on OpenAlex by topic and/or author name (public API, no key).

    - `author` is resolved to an OpenAlex author id first (best name match), then works are
      filtered by that author. An unknown author returns empty `items`, not an error.
    - `query` is a topic/keyword search over titles and abstracts.
    """
    try:
        query, author = _clean(query), _clean(author)
        if not query and not author:
            raise ValueError("give a topic (query) or an author name")
        sort = pick(sort, tuple(SORTS), "cited")
        limit = clamp_int(limit, 5)
        headers = {"User-Agent": USER_AGENT}
        params: dict[str, Any] = {
            "per-page": limit,
            "sort": SORTS[sort],
            "select": "id,display_name,publication_year,cited_by_count,doi,authorships,primary_location",
        }
        filters: list[str] = []
        if sort == "recent":
            # OpenAlex contains records dated in the future; without this they top "newest first".
            filters.append(f"to_publication_date:{date.today().isoformat()}")
        author_name = None
        if author:
            found = requests.get(
                f"{OPENALEX}/authors",
                params={"search": author, "per-page": 1, "select": "id,display_name"},
                headers=headers,
                timeout=TIMEOUT,
            )
            found.raise_for_status()
            matches = found.json().get("results") or []
            if not matches:
                return {"tool": "search_openalex", "query": query, "author": author, "sort": sort,
                        "items": [], "note": "author not found"}
            author_name = matches[0].get("display_name") or author
            filters.append("author.id:" + str(matches[0]["id"]).rsplit("/", 1)[-1])
        if filters:
            params["filter"] = ",".join(filters)
        if query:
            params["search"] = query
        response = requests.get(f"{OPENALEX}/works", params=params, headers=headers, timeout=TIMEOUT)
        response.raise_for_status()
        items = []
        for work in (response.json().get("results") or [])[:limit]:
            names = [a.get("author", {}).get("display_name") for a in work.get("authorships") or []]
            names = [n for n in names if n][:3]
            venue = ((work.get("primary_location") or {}).get("source") or {}).get("display_name") or ""
            items.append({
                "title": work.get("display_name") or "",
                "url": work.get("doi") or work.get("id") or "",
                "source": venue or "openalex.org",
                "summary": f"{work.get('publication_year')}, {work.get('cited_by_count') or 0} citations"
                           + (f", authors: {', '.join(names)}" if names else ""),
                "year": work.get("publication_year"),
                "cited_by": work.get("cited_by_count"),
            })
        return {"tool": "search_openalex", "query": query, "author": author_name or author, "sort": sort, "items": items}
    except Exception as exc:
        return err("search_openalex", exc)
