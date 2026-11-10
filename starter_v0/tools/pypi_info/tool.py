"""pypi_info: tra cứu metadata chính thức của thư viện Python trên PyPI (tool mới phần Bonus).

Nguyên tắc thiết kế (theo RUBRIC C4 & Bonus):
- Không bao giờ raise exception ra ngoài: mọi lỗi đầu vào hoặc lỗi mạng/HTTP 404 đều trả về error dict.
- Kiểm tra `package_name` hợp lệ (không rỗng, chỉ chứa ký tự tên gói hợp lệ) TRƯỚC khi gọi mạng.
- Chuẩn hóa kết quả về khuôn chung {"tool", "package_name", "items": [...]} để tương thích với `format`.
"""
from __future__ import annotations

import re
from typing import Any

import requests

PYPI_URL_TEMPLATE = "https://pypi.org/pypi/{package}/json"
VALID_PACKAGE_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


def _error(package_name: str, message: str, next_step: str) -> dict[str, Any]:
    """Tạo error dict thống nhất cho mọi nhánh lỗi của pypi_info."""
    return {
        "tool": "pypi_info",
        "package_name": package_name,
        "items": [],
        "error": message,
        "next_step": next_step,
    }


def pypi_info(package_name: str) -> dict[str, Any]:
    """Tra cứu phiên bản mới nhất và thông tin gói thư viện Python trên PyPI."""

    # 1) Kiểm tra `package_name`: bắt buộc là chuỗi không rỗng và đúng định dạng tên gói PyPI.
    clean_pkg = package_name.strip() if isinstance(package_name, str) else ""
    if not clean_pkg:
        return _error(
            "",
            "missing_required_param: package_name must be a non-empty string",
            "Call clarify to ask the user which Python package name on PyPI to inspect.",
        )
    if not VALID_PACKAGE_RE.match(clean_pkg):
        return _error(
            clean_pkg,
            f"invalid_param: package_name {package_name!r} contains invalid characters",
            "Pass a valid PyPI package identifier (letters, digits, '.', '_', '-') such as 'langgraph' or 'ragas'.",
        )

    # 2) Gọi PyPI JSON API. Nếu gói không tồn tại (HTTP 404) hoặc lỗi mạng thì trả error dict.
    url = PYPI_URL_TEMPLATE.format(package=clean_pkg)
    try:
        response = requests.get(
            url,
            headers={"Accept": "application/json", "User-Agent": "research-agent-lab"},
            timeout=10,
        )
        response.raise_for_status()
        payload = response.json()
    except Exception as exc:
        return _error(
            clean_pkg,
            f"pypi_api_error: {exc}",
            "Verify the exact package name on PyPI, or fall back to github_search / lookup.",
        )

    # 3) Trích thông tin từ nhánh `info` của PyPI JSON payload.
    info = payload.get("info") if isinstance(payload, dict) else None
    if not isinstance(info, dict):
        info = {}

    name = str(info.get("name") or clean_pkg).strip()
    version = str(info.get("version") or "unknown").strip()
    summary = str(info.get("summary") or "No summary provided.").strip()
    requires_python = str(info.get("requires_python") or "any").strip()
    license_name = str(info.get("license") or "Unknown").strip()
    package_url = str(
        info.get("package_url")
        or info.get("project_url")
        or f"https://pypi.org/project/{clean_pkg}/"
    ).strip()

    item = {
        "title": f"{name}=={version}",
        "url": package_url,
        "source": "pypi.org",
        "version": version,
        "requires_python": requires_python,
        "license": license_name,
        "summary": f"{summary} (latest: {version}, requires_python: {requires_python})",
    }

    return {"tool": "pypi_info", "package_name": clean_pkg, "items": [item]}
