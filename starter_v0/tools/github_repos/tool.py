from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from typing import Any

import requests

from tools._shared import TIMEOUT, err

_VALID_SORT_BY = {"stars", "hot", "updated", "forks"}
_TIMEFRAME_DAYS = {
    "day": 1,
    "week": 7,
    "month": 30,
    "year": 365,
}


def _coerce_int(value: Any, default: int) -> int:
    try:
        if value is None or value == "":
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def _stars_per_day(stars: int, created_at: str | None, now: datetime) -> float | None:
    if not created_at:
        return None
    try:
        created = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        age_days = max((now - created).total_seconds() / 86400.0, 1.0)
        return round(stars / age_days, 2)
    except ValueError:
        return None


def search_github_repos(
    query: str = "",
    sort_by: str = "stars",
    timeframe: str = "all",
    min_stars: int = 0,
    language: str = "",
    limit: int = 5,
) -> dict[str, Any]:
    """Search GitHub repositories by keyword, stars, language, or recent velocity."""
    try:
        clean_query = str(query or "").strip()
        clean_lang = str(language or "").strip()
        safe_sort = sort_by if sort_by in _VALID_SORT_BY else "stars"
        safe_timeframe = timeframe if (timeframe == "all" or timeframe in _TIMEFRAME_DAYS) else "all"
        if safe_sort == "hot" and safe_timeframe == "all":
            safe_timeframe = "week"

        safe_min_stars = max(_coerce_int(min_stars, 0), 0)
        safe_limit = min(max(_coerce_int(limit, 5), 1), 20)

        now = datetime.now(timezone.utc)
        qualifiers: list[str] = []
        if clean_query:
            qualifiers.append(clean_query)
        if clean_lang:
            qualifiers.append(f"language:{clean_lang}")
        if safe_min_stars > 0:
            qualifiers.append(f"stars:>={safe_min_stars}")
        if safe_timeframe in _TIMEFRAME_DAYS:
            since = (now - timedelta(days=_TIMEFRAME_DAYS[safe_timeframe])).strftime("%Y-%m-%d")
            qualifiers.append(f"created:>={since}")

        if not qualifiers:
            return {
                "tool": "github_repos",
                "query": clean_query,
                "sort_by": safe_sort,
                "timeframe": safe_timeframe,
                "items": [],
            }

        github_sort = "stars" if safe_sort == "hot" else safe_sort
        headers = {"Accept": "application/vnd.github+json"}
        token = os.getenv("GITHUB_TOKEN", "").strip()
        if token:
            headers["Authorization"] = f"Bearer {token}"

        response = requests.get(
            "https://api.github.com/search/repositories",
            params={
                "q": " ".join(qualifiers),
                "sort": github_sort,
                "order": "desc",
                "per_page": safe_limit,
            },
            headers=headers,
            timeout=TIMEOUT,
        )
        response.raise_for_status()
        data = response.json()

        items: list[dict[str, Any]] = []
        for repo in data.get("items", [])[:safe_limit]:
            stars = int(repo.get("stargazers_count") or 0)
            created_at = repo.get("created_at")
            items.append({
                "title": repo.get("full_name") or repo.get("name"),
                "url": repo.get("html_url"),
                "source": "github.com",
                "summary": repo.get("description") or "",
                "stars": stars,
                "forks": int(repo.get("forks_count") or 0),
                "language": repo.get("language"),
                "created_at": created_at,
                "pushed_at": repo.get("pushed_at"),
                "stars_per_day": _stars_per_day(stars, created_at, now),
            })

        return {
            "tool": "github_repos",
            "query": clean_query,
            "sort_by": safe_sort,
            "timeframe": safe_timeframe,
            "items": items,
        }
    except Exception as exc:
        return err("github_repos", exc)

