from __future__ import annotations

import re
from typing import Any

import requests

from tools._shared import TIMEOUT, err

PACKAGE_PATTERN = re.compile(r"[A-Za-z0-9](?:[A-Za-z0-9._-]{0,98}[A-Za-z0-9])?")


def get_pypi_package(package: str = "") -> dict[str, Any]:
    try:
        if not isinstance(package, str):
            raise ValueError("package must be a string")
        package = package.strip()
        if not PACKAGE_PATTERN.fullmatch(package):
            raise ValueError("package must be a PyPI project name, e.g. requests; no URL or version specifier")

        response = requests.get(
            f"https://pypi.org/pypi/{package}/json",
            headers={"Accept": "application/json", "User-Agent": "Day03-Research-Agent"},
            timeout=TIMEOUT,
        )
        response.raise_for_status()
        data = response.json()
        info = data.get("info") if isinstance(data, dict) else None
        if not isinstance(info, dict) or "version" not in info:
            raise ValueError("PyPI response has no info.version")

        files = data.get("urls") or []
        uploaded = next((f.get("upload_time_iso_8601") for f in files if f.get("upload_time_iso_8601")), None)
        return {
            "tool": "pypi_package",
            "items": [{
                "title": info.get("name") or package,
                "url": info.get("package_url") or f"https://pypi.org/project/{package}/",
                "source": "pypi.org",
                "summary": info.get("summary") or "",
                "latest_version": info["version"],
                "requires_python": info.get("requires_python"),
                "released_at": uploaded,
            }],
        }
    except Exception as exc:
        return err("pypi_package", exc)
