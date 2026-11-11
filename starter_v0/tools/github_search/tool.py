from __future__ import annotations

import os
import re
from typing import Any

import requests

from tools._shared import TIMEOUT, err

SEARCH_URL = "https://api.github.com/search/repositories"
ALLOWED_SORT = {"stars", "forks", "updated", "best_match"}
ALLOWED_ORDER = {"desc", "asc"}
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _repo_item(repo: dict[str, Any]) -> dict[str, Any]:
    stars = repo.get("stargazers_count") or 0
    forks = repo.get("forks_count") or 0
    language = repo.get("language") or ""
    description = repo.get("description") or ""
    return {
        "title": repo.get("full_name") or "",
        "url": repo.get("html_url") or "",
        "source": "github.com",
        "description": description,
        "stars": stars,
        "forks": forks,
        "language": language,
        "topics": repo.get("topics") or [],
        "created_at": repo.get("created_at") or "",
        "updated_at": repo.get("updated_at") or "",
        "summary": f"★{stars} · forks {forks} · {language or 'n/a'} — {description}".strip(" —"),
    }


def github_search(
    query: str = "",
    sort: str = "stars",
    order: str = "desc",
    language: str = "",
    created_after: str = "",
    limit: int = 5,
) -> dict[str, Any]:
    """Search GitHub repositories. GITHUB_TOKEN is optional (raises the rate limit 10 -> 30 req/min)."""
    try:
        query = (query or "").strip()
        if not query:
            raise ValueError("query is required")
        sort = sort if sort in ALLOWED_SORT else "stars"
        order = order if order in ALLOWED_ORDER else "desc"
        if created_after and not DATE_RE.match(created_after.strip()):
            raise ValueError(f"created_after must be YYYY-MM-DD, got {created_after!r}")
        try:
            per_page = max(1, min(int(limit or 5), 20))
        except (TypeError, ValueError):
            per_page = 5

        q = query
        if language:
            q += f" language:{language.strip()}"
        if created_after:
            q += f" created:>={created_after.strip()}"

        params: dict[str, Any] = {"q": q, "per_page": per_page}
        if sort != "best_match":
            params["sort"] = sort
            params["order"] = order

        headers = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
        token = os.getenv("GITHUB_TOKEN")
        if token:
            headers["Authorization"] = f"Bearer {token}"

        response = requests.get(SEARCH_URL, params=params, headers=headers, timeout=TIMEOUT)
        if response.status_code in (403, 429):
            raise RuntimeError(f"GitHub rate limit or permission error (HTTP {response.status_code}); set GITHUB_TOKEN")
        response.raise_for_status()
        data = response.json()
        items = [_repo_item(repo) for repo in data.get("items", [])[:per_page]]
        return {
            "tool": "github_search",
            "query": query,
            "q": q,
            "sort": sort,
            "order": order,
            "total_count": data.get("total_count", 0),
            "items": items,
        }
    except Exception as exc:
        return err("github_search", exc)
