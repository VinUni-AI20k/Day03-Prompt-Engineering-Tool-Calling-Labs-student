from __future__ import annotations

from typing import Any

import requests

from tools._shared import TIMEOUT, err

ALLOWED_SORTS = {"stars", "updated", "help-wanted-issues"}


def search_github_repos(
    query: str = "",
    language: str = "",
    sort: str = "stars",
    max_results: int = 5,
) -> dict[str, Any]:
    try:
        clean_query = (query or "").strip()
        if not clean_query:
            raise ValueError("query must not be empty")

        clean_sort = (sort or "stars").strip()
        if clean_sort not in ALLOWED_SORTS:
            raise ValueError(f"Invalid sort {sort!r}; must be one of {sorted(ALLOWED_SORTS)}")

        limit = int(max_results or 5)
        if limit <= 0 or limit > 30:
            raise ValueError("max_results must be between 1 and 30")

        clean_lang = (language or "").strip()
        full_query = f"{clean_query} language:{clean_lang}" if clean_lang else clean_query

        response = requests.get(
            "https://api.github.com/search/repositories",
            params={
                "q": full_query,
                "sort": clean_sort,
                "order": "desc",
                "per_page": limit,
            },
            headers={
                "Accept": "application/vnd.github+json",
                "User-Agent": "AI20k-Day03-Research-Agent/1.0",
            },
            timeout=TIMEOUT,
        )
        response.raise_for_status()
        data = response.json()

        items = []
        for repo in (data.get("items") or [])[:limit]:
            items.append({
                "title": repo.get("full_name") or repo.get("name"),
                "url": repo.get("html_url"),
                "source": "github.com",
                "summary": repo.get("description") or "",
                "stars": repo.get("stargazers_count", 0),
                "language": repo.get("language"),
            })

        return {
            "tool": "search_github_repos",
            "query": clean_query,
            "language": clean_lang or None,
            "sort": clean_sort,
            "items": items,
        }
    except Exception as exc:
        return err("search_github_repos", exc)
