from __future__ import annotations

import re
from typing import Any

import requests

from tools._shared import TIMEOUT, err

API = "https://pypi.org/pypi/{package}/json"
API_VERSION = "https://pypi.org/pypi/{package}/{version}/json"
PACKAGE_RE = re.compile(r"^[A-Za-z0-9_.-]+$")


def _fail(code: str, message: str, **extra: Any) -> dict[str, Any]:
    return {"tool": "pypi_package", "error": code, "message": message, **extra}


def get_pypi_package(package: str = "", version: str = "") -> dict[str, Any]:
    try:
        # 1. Validate TRƯỚC khi gọi mạng
        pkg = (package or "").strip().lower()
        # Loại bỏ nếu model nhầm lẫn truyền cả lệnh pip install hoặc dấu so sánh
        if pkg.startswith("pip install"):
            pkg = pkg.removeprefix("pip install").strip()
        if "==" in pkg:
            pkg_name, _, v = pkg.partition("==")
            pkg = pkg_name.strip()
            if not version:
                version = v.strip()

        if not pkg or not PACKAGE_RE.match(pkg):
            return _fail("invalid_package", "Tên package không hợp lệ", package=package)

        ver = (version or "").strip()
        url = API_VERSION.format(package=pkg, version=ver) if ver else API.format(package=pkg)

        # 2. Gọi HTTP
        resp = requests.get(url, timeout=TIMEOUT)
        if resp.status_code == 404:
            return _fail("not_found", f"Không tìm thấy package '{pkg}' (hoặc version '{ver}') trên PyPI", package=pkg, version=ver)
        resp.raise_for_status()
        data = resp.json()

        info = data.get("info", {})
        actual_ver = info.get("version", ver)
        urls = data.get("urls", [])
        release_date = urls[0].get("upload_time_iso_8601") if urls else None

        lic = info.get("license") or ""
        if len(lic) > 100:
            lic = lic[:97] + "..."

        # 3. Trả kết quả map theo đúng hợp đồng
        return {
            "tool": "pypi_package",
            "package": info.get("name", pkg),
            "version": actual_ver,
            "summary": info.get("summary"),
            "license": lic,
            "requires_python": info.get("requires_python"),
            "release_date": release_date,
            "home_page": info.get("home_page"),
            "project_urls": info.get("project_urls") or {},
            "install": f"pip install {pkg}=={actual_ver}",
        }
    except Exception as exc:
        return err("pypi_package", exc)