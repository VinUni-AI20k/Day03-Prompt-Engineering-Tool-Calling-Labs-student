from __future__ import annotations

import re
from typing import Any

import requests

from tools._shared import TIMEOUT, err


REPO_PATTERN = re.compile(
    r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?/[A-Za-z0-9_.-]{1,100}"
)


def get_github_repo(repo: str = "") -> dict[str, Any]:
    try:
        if not isinstance(repo, str):
            raise ValueError("repo must be a string in owner/repo format")
        repo = repo.strip()
        if (
            not REPO_PATTERN.fullmatch(repo)
            or repo.split("/")[-1] in {".", ".."}
            or repo.lower().endswith(".git")
        ):
            raise ValueError("repo must be owner/repo, e.g. psf/requests; no URL or .git suffix")

        response = requests.get(
            f"https://api.github.com/repos/{repo}",
            headers={
                "Accept": "application/vnd.github+json",
                "User-Agent": "Day03-Research-Agent",
                "X-GitHub-Api-Version": "2026-03-10",
            },
            timeout=TIMEOUT,
        )
        response.raise_for_status()
        data = response.json()
        if not isinstance(data, dict):
            raise ValueError("GitHub response must be a JSON object")

        return {
            "tool": "github_repo",
            "items": [{
                "title": data["full_name"],
                "url": data["html_url"],
                "source": "github.com",
                "summary": data.get("description") or "",
                "stars": data["stargazers_count"],
                "forks": data["forks_count"],
                "language": data.get("language"),
                "updated_at": data.get("updated_at"),
            }],
        }
    except Exception as exc:
        return err("github_repo", exc)