from __future__ import annotations

import os
from typing import Any

import requests

from tools._shared import TIMEOUT, err


SEARCH_URL = "https://api.github.com/search/repositories"


def search_github(query: str = "", sort: str = "best_match", order: str = "desc", max_results: int = 5) -> dict[str, Any]:
    """Search public GitHub repositories; does not read files or execute code."""
    try:
        if not isinstance(query, str) or not 1 <= len(query.strip()) <= 240:
            raise ValueError("query must contain 1 to 240 characters")
        if not isinstance(sort, str) or sort not in {"best_match", "stars", "forks", "updated"}:
            raise ValueError("sort must be best_match, stars, forks or updated")
        if not isinstance(order, str) or order not in {"asc", "desc"}:
            raise ValueError("order must be asc or desc")
        if type(max_results) is not int or not 1 <= max_results <= 10:
            raise ValueError("max_results must be an integer from 1 to 10")
        query = query.strip()
        params: dict[str, Any] = {"q": f"{query} is:public", "per_page": max_results, "order": order}
        if sort != "best_match":
            params["sort"] = sort
        headers = {"Accept": "application/vnd.github+json", "User-Agent": "ResearchAgentToolEval/1.0"}
        token = os.getenv("GITHUB_TOKEN", "").strip()
        if token:
            headers["Authorization"] = f"Bearer {token}"
        response = requests.get(SEARCH_URL, params=params, headers=headers, timeout=TIMEOUT)
        response.raise_for_status()
        data = response.json()
        if not isinstance(data.get("items"), list):
            raise ValueError("GitHub returned an invalid repository search response")
        items = []
        for repo in data["items"]:
            if repo.get("private") or not repo.get("full_name") or not repo.get("html_url"):
                continue
            license_info = repo.get("license") or {}
            items.append({
                "title": repo["full_name"], "url": repo["html_url"], "source": "github.com",
                "summary": repo.get("description") or "Không có mô tả.",
                "stars": repo.get("stargazers_count", 0), "forks": repo.get("forks_count", 0),
                "language": repo.get("language"), "license": license_info.get("spdx_id"),
                "topics": repo.get("topics") or [], "archived": repo.get("archived", False),
                "date": repo.get("updated_at"),
            })
        return {
            "tool": "github_search", "query": query, "sort": sort, "order": order,
            "total_count": data.get("total_count", 0),
            "incomplete_results": data.get("incomplete_results", False),
            "items": items[:max_results],
        }
    except Exception as exc:
        return {**err("github_search", exc), "items": []}
