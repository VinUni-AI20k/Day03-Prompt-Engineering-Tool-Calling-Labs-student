"""hn_search: tìm kiếm thảo luận công nghệ trên Hacker News qua Algolia API (tool mới phần Bonus).

Nguyên tắc thiết kế (theo RUBRIC C4 & Bonus):
- Không bao giờ raise exception ra ngoài: mọi lỗi đầu vào hoặc lỗi mạng đều trả về error dict.
- Kiểm tra `query`, `sort_by` (chỉ nhận 'points' hoặc 'date') và `limit` TRƯỚC khi gọi mạng.
- Chuẩn hóa kết quả về khuôn chung {"tool", "query", "items": [...]} để tương thích với `format`.
"""
from __future__ import annotations

from typing import Any

import requests

HN_SEARCH_BY_POINTS_URL = "https://hn.algolia.com/api/v1/search"
HN_SEARCH_BY_DATE_URL = "https://hn.algolia.com/api/v1/search_by_date"
ALLOWED_SORT_BY = {"points", "date"}
DEFAULT_LIMIT = 5
MAX_LIMIT = 10


def _error(query: str, message: str, next_step: str) -> dict[str, Any]:
    """Tạo error dict thống nhất cho mọi nhánh lỗi của hn_search."""
    return {
        "tool": "hn_search",
        "query": query,
        "items": [],
        "error": message,
        "next_step": next_step,
    }


def hn_search(query: str, sort_by: str = "points", limit: int = DEFAULT_LIMIT) -> dict[str, Any]:
    """Tìm bài thảo luận trên Hacker News theo điểm (points) hoặc ngày đăng (date)."""

    # 1) Kiểm tra `query`: bắt buộc là chuỗi không rỗng.
    clean_query = query.strip() if isinstance(query, str) else ""
    if not clean_query:
        return _error(
            "",
            "missing_required_param: query must be a non-empty string",
            "Call clarify to ask the user which topic to search on Hacker News.",
        )

    # 2) Kiểm tra `sort_by`: chỉ chấp nhận 'points' hoặc 'date'.
    clean_sort = sort_by.strip().lower() if isinstance(sort_by, str) and sort_by.strip() else "points"
    if clean_sort not in ALLOWED_SORT_BY:
        return _error(
            clean_query,
            f"invalid_param: sort_by must be one of {sorted(ALLOWED_SORT_BY)}, got {sort_by!r}",
            "Retry hn_search with sort_by='points' or sort_by='date'.",
        )

    # 3) Kiểm tra `limit`: None -> mặc định 5; <= 0 -> báo lỗi; > 10 -> ép về 10.
    try:
        parsed_limit = DEFAULT_LIMIT if limit is None else int(limit)
    except (TypeError, ValueError):
        parsed_limit = DEFAULT_LIMIT
    if parsed_limit <= 0:
        return _error(
            clean_query,
            f"invalid_param: limit must be a positive integer, got {limit!r}",
            f"Retry hn_search with limit between 1 and {MAX_LIMIT}.",
        )
    clamped_limit = min(parsed_limit, MAX_LIMIT)

    # 4) Chọn endpoint tương ứng với tiêu chí sắp xếp.
    endpoint = HN_SEARCH_BY_DATE_URL if clean_sort == "date" else HN_SEARCH_BY_POINTS_URL

    # 5) Gọi API và bắt mọi lỗi mạng / HTTP / JSON.
    try:
        response = requests.get(
            endpoint,
            params={"query": clean_query, "tags": "story", "hitsPerPage": clamped_limit},
            headers={"Accept": "application/json", "User-Agent": "research-agent-lab"},
            timeout=10,
        )
        response.raise_for_status()
        payload = response.json()
    except Exception as exc:
        return _error(
            clean_query,
            f"hn_api_error: {exc}",
            "Tell the user Hacker News search is temporarily unavailable, or fall back to lookup.",
        )

    # 6) Trích danh sách `hits` từ phản hồi của Algolia.
    raw_hits = payload.get("hits") if isinstance(payload, dict) else None
    if not isinstance(raw_hits, list):
        raw_hits = []

    items = []
    for hit in raw_hits[:clamped_limit]:
        if not isinstance(hit, dict):
            continue
        object_id = str(hit.get("objectID") or "").strip()
        hn_discussion_url = f"https://news.ycombinator.com/item?id={object_id}" if object_id else ""
        url = str(hit.get("url") or hn_discussion_url).strip()
        title = str(hit.get("title") or "Untitled HN Story").strip()
        author = str(hit.get("author") or "unknown").strip()
        try:
            points = int(hit.get("points") or 0)
        except (TypeError, ValueError):
            points = 0
        try:
            comments = int(hit.get("num_comments") or 0)
        except (TypeError, ValueError):
            comments = 0
        items.append({
            "title": title,
            "url": url,
            "source": "news.ycombinator.com",
            "points": points,
            "comments": comments,
            "author": author,
            "summary": f"HN story by {author} ({points} points, {comments} comments).",
        })

    return {"tool": "hn_search", "query": clean_query, "sort_by": clean_sort, "items": items}
