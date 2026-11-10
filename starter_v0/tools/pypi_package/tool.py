from __future__ import annotations

import re
from typing import Any

import requests

from tools._shared import TIMEOUT, err

_VALID_PKG_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


def _as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "on"}
    return bool(value)


def _latest_release_date(releases: dict[str, Any], version: str) -> str | None:
    files = releases.get(version)
    if not isinstance(files, list) or not files:
        return None
    first = files[0]
    if not isinstance(first, dict):
        return None
    return first.get("upload_time_iso_8601") or first.get("upload_time")


def get_pypi_package(package_name: str = "", include_releases: bool = False) -> dict[str, Any]:
    """Fetch package metadata (latest version, license, Python requirement, URLs) from PyPI."""
    try:
        clean_name = str(package_name or "").strip()
        if not clean_name:
            raise ValueError("package_name is required")
        if not _VALID_PKG_RE.match(clean_name):
            raise ValueError(f"Invalid PyPI package name: {clean_name!r}")

        response = requests.get(
            f"https://pypi.org/pypi/{clean_name}/json",
            headers={"Accept": "application/json"},
            timeout=TIMEOUT,
        )
        response.raise_for_status()
        data = response.json()

        info = data.get("info") or {}
        releases = data.get("releases") or {}
        name = info.get("name") or clean_name
        version = info.get("version") or ""
        license_name = info.get("license_expression") or info.get("license") or ""
        package_url = info.get("package_url") or info.get("project_url") or f"https://pypi.org/project/{name}/"
        release_date = _latest_release_date(releases, version) if isinstance(releases, dict) else None

        item: dict[str, Any] = {
            "title": f"{name} ({version})" if version else name,
            "url": package_url,
            "source": "pypi.org",
            "summary": info.get("summary") or "",
            "name": name,
            "version": version,
            "license": license_name,
            "requires_python": info.get("requires_python") or "",
            "author": info.get("author") or info.get("author_email") or "",
            "latest_release_date": release_date,
            "project_urls": info.get("project_urls") or {},
        }

        result: dict[str, Any] = {
            "tool": "pypi_package",
            "package_name": name,
            "version": version,
            "items": [item],
        }
        if _as_bool(include_releases) and isinstance(releases, dict):
            result["recent_versions"] = list(releases.keys())[-5:]

        return result
    except Exception as exc:
        return err("pypi_package", exc)

