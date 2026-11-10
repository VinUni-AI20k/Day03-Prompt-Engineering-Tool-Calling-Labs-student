from __future__ import annotations

import time
from typing import Any

import requests

from tools._shared import TIMEOUT, err

API_RELEVANCE = "https://hn.algolia.com/api/v1/search"
API_DATE = "https://hn.algolia.com/api/v1/search_by_date"

TIMEFRAME_SECONDS = {
    "day": 86400,
    "week": 7 * 86400,
    "month": 30 * 86400,
    "year": 365 * 86400,
}


def _fail(code: str, message: str, **extra: Any) -> dict[str, Any]:
    return {"tool": "hn_search", "error": code, "message": message, **extra}


def search_hacker_news(
    query: str = "",
    sort: str = "relevance",
    timeframe: str = "week",
    limit: int = 5,
) -> dict[str, Any]:
    try:
        # 1. Validate
        q = (query or "").strip()
        if not q:
            return _fail("invalid_query", "query tìm kiếm không được để trống")

        # Ép kiểu an toàn cho limit và kẹp trong khoảng 1..20
        try:
            lim = int(limit)
        except (ValueError, TypeError):
            lim = 5
        lim = max(1, min(20, lim))

        # Kiểm tra sort
        s = (sort or "relevance").strip().lower()
        if s not in ("relevance", "date"):
            s = "relevance"

        # Kiểm tra timeframe
        tf = (timeframe or "week").strip().lower()
        if tf not in ("day", "week", "month", "year", "all"):
            tf = "week"

        url = API_DATE if s == "date" else API_RELEVANCE
        params: dict[str, Any] = {
            "query": q,
            "tags": "story",
            "hitsPerPage": lim,
        }

        if tf != "all" and tf in TIMEFRAME_SECONDS:
            since_ts = int(time.time() - TIMEFRAME_SECONDS[tf])
            params["numericFilters"] = f"created_at_i>{since_ts}"

        # 2. Gọi HTTP
        resp = requests.get(url, params=params, timeout=TIMEOUT)
        resp.raise_for_status()
        data = resp.json()

        # 3. Format kết quả
        results = []
        for hit in data.get("hits", []):
            obj_id = hit.get("objectID")
            hn_url = f"https://news.ycombinator.com/item?id={obj_id}"
            results.append({
                "title": hit.get("title") or "[No Title]",
                "url": hit.get("url") or hn_url,
                "hn_url": hn_url,
                "author": hit.get("author"),
                "points": hit.get("points", 0),
                "num_comments": hit.get("num_comments", 0),
                "created_at": hit.get("created_at"),
            })

        return {
            "tool": "hn_search",
            "query": q,
            "sort": s,
            "timeframe": tf,
            "results": results,
        }
    except Exception as exc:
        return err("hn_search", exc)