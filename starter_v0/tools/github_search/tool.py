"""github_search: tìm repository công khai trên GitHub (tool mới của nhóm, CP3).

Nguyên tắc thiết kế (theo RUBRIC C4):
- Không bao giờ raise exception ra ngoài. Mọi lỗi (input xấu từ model, mất mạng,
  HTTP 4xx/5xx, JSON lạ) đều trả về dict có "error" và "next_step" để agent biết
  bước tiếp theo, thay vì làm sập vòng lặp agent.
- Kiểm tra input TRƯỚC khi gọi mạng: input xấu thì không tốn request nào.
- Output dùng chung khuôn với các tool có sẵn: {"tool", "query", "items": [...]},
  mỗi item có title / url / source / summary để tool `format` dùng lại được.
"""
from __future__ import annotations

import os
from typing import Any

import requests

GITHUB_SEARCH_URL = "https://api.github.com/search/repositories"
DEFAULT_LIMIT = 5
MAX_LIMIT = 10  # Giới hạn trên để agent không kéo về quá nhiều kết quả.


def _error(query: str, message: str, next_step: str) -> dict[str, Any]:
    """Tạo error dict thống nhất cho mọi nhánh lỗi."""
    return {
        "tool": "github_search",
        "query": query,
        "items": [],
        "error": message,
        "next_step": next_step,
    }


def github_search(query: str, language: str = "", limit: int = DEFAULT_LIMIT) -> dict[str, Any]:
    """Tìm repo GitHub theo từ khóa, sắp xếp theo số sao giảm dần."""

    # 1) Kiểm tra `query`: model có thể gửi "", "   ", None hoặc sai kiểu (vd số 123).
    clean_query = query.strip() if isinstance(query, str) else ""
    if not clean_query:
        return _error(
            "",
            "missing_required_param: query must be a non-empty string",
            "Call clarify to ask the user which GitHub topic or keyword to search.",
        )

    # 2) Kiểm tra `limit`: model có thể gửi "3" (string), None, 0, số âm hoặc 999.
    #    - None / không ép được sang int -> dùng mặc định 5.
    #    - <= 0 -> báo lỗi rõ ràng (không âm thầm đổi thành 5 như bug của timeline).
    #    - > 10 -> ép về 10.
    try:
        parsed_limit = DEFAULT_LIMIT if limit is None else int(limit)
    except (TypeError, ValueError):
        parsed_limit = DEFAULT_LIMIT
    if parsed_limit <= 0:
        return _error(
            clean_query,
            f"invalid_param: limit must be a positive integer, got {limit!r}",
            f"Retry github_search with limit between 1 and {MAX_LIMIT}.",
        )
    clamped_limit = min(parsed_limit, MAX_LIMIT)

    # 3) Ghép cú pháp tìm kiếm của GitHub: "<từ khóa> language:<ngôn ngữ>".
    clean_lang = language.strip() if isinstance(language, str) else ""
    full_query = f"{clean_query} language:{clean_lang}" if clean_lang else clean_query

    # 4) GITHUB_TOKEN là TÙY CHỌN: không có vẫn chạy (giới hạn khoảng 10 request/phút),
    #    có thì được nâng hạn mức. Vì vậy thiếu token KHÔNG phải là lỗi.
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "research-agent-lab"}
    token = os.getenv("GITHUB_TOKEN", "").strip()
    if token:
        headers["Authorization"] = f"Bearer {token}"

    # 5) Gọi API. Mọi exception (timeout, mất mạng, HTTP 403/429 do rate limit,
    #    JSON hỏng) đều bị bắt lại và đổi thành error dict.
    try:
        response = requests.get(
            GITHUB_SEARCH_URL,
            params={"q": full_query, "sort": "stars", "order": "desc", "per_page": clamped_limit},
            headers=headers,
            timeout=10,
        )
        response.raise_for_status()
        payload = response.json()
    except Exception as exc:
        return _error(
            full_query,
            f"github_api_error: {exc}",
            "Tell the user GitHub search is temporarily unavailable, or fall back to lookup.",
        )

    # 6) Phòng trường hợp API trả về khuôn lạ (không phải dict / thiếu "items").
    raw_items = payload.get("items") if isinstance(payload, dict) else None
    if not isinstance(raw_items, list):
        raw_items = []

    # 7) Map từng repo sang khuôn item chung. Dùng `or` để trường None không làm vỡ code.
    items = []
    for repo in raw_items[:clamped_limit]:
        if not isinstance(repo, dict):
            continue  # Bỏ qua phần tử hỏng thay vì crash.
        try:
            stars = int(repo.get("stargazers_count") or 0)
        except (TypeError, ValueError):
            stars = 0
        items.append({
            "title": repo.get("full_name") or repo.get("name") or "unknown",
            "url": repo.get("html_url") or "",
            "source": "github.com",
            "stars": stars,
            "language": repo.get("language") or "Unknown",
            "summary": (repo.get("description") or "No description provided.").strip(),
        })

    return {"tool": "github_search", "query": full_query, "items": items}
