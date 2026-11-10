from __future__ import annotations

from typing import Any

import requests

from tools._shared import TIMEOUT, err


GITHUB_REPOSITORY_SEARCH_URL = "https://api.github.com/search/repositories"
ALLOWED_SORTS = {"best_match", "stars", "forks", "help_wanted_issues", "updated"}


def search_github_repositories(
    query: str = "",
    language: str = "",
    sort: str = "best_match",
    limit: int = 5,
) -> dict[str, Any]:
    """Search public GitHub repositories and return research-friendly metadata."""
    try:
        if not isinstance(query, str) or not query.strip():
            raise ValueError("query must be a non-empty string")
        if not isinstance(language, str):
            raise ValueError("language must be a string")
        if sort not in ALLOWED_SORTS:
            raise ValueError(f"sort must be one of: {', '.join(sorted(ALLOWED_SORTS))}")
        if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= 10:
            raise ValueError("limit must be an integer from 1 to 10")

        normalized_query = " ".join(query.split())
        normalized_language = language.strip()
        api_query = normalized_query
        if normalized_language:
            api_query += f" language:{normalized_language}"

        params: dict[str, Any] = {"q": api_query, "per_page": limit}
        if sort != "best_match":
            params.update({"sort": sort, "order": "desc"})

        response = requests.get(
            GITHUB_REPOSITORY_SEARCH_URL,
            params=params,
            headers={
                "Accept": "application/vnd.github+json",
                "User-Agent": "Day03-Research-Agent",
                "X-GitHub-Api-Version": "2022-11-28",
            },
            timeout=TIMEOUT,
        )
        response.raise_for_status()
        payload = response.json()

        items = []
        for repository in payload.get("items", [])[:limit]:
            items.append({
                "name": repository.get("full_name", ""),
                "title": repository.get("full_name", ""),
                "url": repository.get("html_url", ""),
                "source": "github.com",
                "summary": repository.get("description") or "",
                "language": repository.get("language"),
                "stars": repository.get("stargazers_count", 0),
                "forks": repository.get("forks_count", 0),
                "updated_at": repository.get("updated_at"),
            })

        return {
            "tool": "github_search",
            "query": normalized_query,
            "language": normalized_language,
            "total_count": payload.get("total_count", len(items)),
            "items": items,
        }
    except Exception as exc:
        return err("github_search", exc)
