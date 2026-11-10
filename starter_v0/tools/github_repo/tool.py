from __future__ import annotations

import os
import re
from typing import Any

import requests

from tools._shared import TIMEOUT, err

API = "https://api.github.com/repos/{repo}"
REPO_RE = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")


def _fail(code: str, message: str, **extra: Any) -> dict[str, Any]:
    return {"tool": "github_repo", "error": code, "message": message, **extra}


def get_github_repo(repo: str = "", include_readme: bool = False) -> dict[str, Any]:
    try:
        # 1. Validate TRƯỚC khi gọi mạng
        repo = (repo or "").strip().removeprefix("https://github.com/").strip("/")
        if not REPO_RE.match(repo):
            return _fail("invalid_repo", "repo phải có dạng owner/name", repo=repo)

        headers = {"Accept": "application/vnd.github+json"}
        if os.getenv("GITHUB_TOKEN"):
            headers["Authorization"] = f"Bearer {os.getenv('GITHUB_TOKEN')}"

        # 2. Gọi API bằng requests.get (để fake_http mock được)
        resp = requests.get(API.format(repo=repo), headers=headers, timeout=TIMEOUT)
        if resp.status_code == 404:
            return _fail("not_found", f"Không tìm thấy repo {repo}", repo=repo)
        if resp.status_code in (403, 429):
            return _fail("rate_limited", "GitHub rate limit", repo=repo)
        resp.raise_for_status()
        data = resp.json()

        # 3. Map field theo hợp đồng
        result = {
            "tool": "github_repo",
            "repo": data.get("full_name", repo),
            "description": data.get("description"),
            "stars": data.get("stargazers_count"),
            "forks": data.get("forks_count"),
            "open_issues": data.get("open_issues_count"),
            "language": data.get("language"),
            "license": (data.get("license") or {}).get("spdx_id"),
            "archived": data.get("archived"),
            "pushed_at": data.get("pushed_at"),
            "url": data.get("html_url"),
        }
        if include_readme:
            r = requests.get(API.format(repo=repo) + "/readme",
                             headers={**headers, "Accept": "application/vnd.github.raw"}, timeout=TIMEOUT)
            if r.status_code == 200:
                result["readme_excerpt"] = r.text[:1500]
        return result
    except Exception as exc:  # 4. Không bao giờ raise
        return err("github_repo", exc)