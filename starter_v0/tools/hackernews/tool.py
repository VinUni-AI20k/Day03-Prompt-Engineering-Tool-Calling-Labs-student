"""Hacker News search tool: tech-community signal (stories + discussion volume).

Design notes
- Read-only (`side_effect: false`), no API key: the Algolia HN Search API is public.
  It exposes the same stories as news.ycombinator.com, but sorted by relevance or date.
- `sort` picks the endpoint: "relevance" -> /search, "date" -> /search_by_date.
- The model is the untrusted caller: args are validated BEFORE the request, and every
  failure returns an error dict (`tools._shared.err`), never raises.
- Ask HN / Show HN posts often have `url: null`; those fall back to the HN item page so
  every item still has a clickable, citable URL.
"""
from __future__ import annotations

import html
import re
from typing import Any

import requests

from tools._shared import TIMEOUT, domain, err

ALLOWED_SORTS = ("relevance", "date")
MAX_LIMIT = 20
MAX_TEXT_CHARS = 500
USER_AGENT = "AI20k-Day03-Research-Agent/1.0 (hackernews search tool)"
API_ROOT = "https://hn.algolia.com/api/v1"
SORT_ENDPOINTS = {"relevance": f"{API_ROOT}/search", "date": f"{API_ROOT}/search_by_date"}


def _clean_args(query: Any, sort: Any, limit: Any) -> tuple[str, str, int]:
    """Validate model-supplied args. Raises, but the caller converts it to an error dict."""
    if not isinstance(query, str):
        raise TypeError(f"query must be a string, got {type(query).__name__}")
    text = query.strip()
    if not text:
        raise ValueError("query is empty; pass keywords, e.g. 'AI agents'")

    normalized_sort = sort.strip().lower() if isinstance(sort, str) else ""
    if normalized_sort not in ALLOWED_SORTS:
        raise ValueError(f"sort must be one of {list(ALLOWED_SORTS)}, got {sort!r}")

    # bool is a subclass of int, so reject it explicitly: True/False are not counts.
    if isinstance(limit, bool) or not isinstance(limit, int):
        raise TypeError(f"limit must be an integer, got {type(limit).__name__}")
    if not 1 <= limit <= MAX_LIMIT:
        raise ValueError(f"limit must be between 1 and {MAX_LIMIT}, got {limit}")
    return text, normalized_sort, limit


def _plain_text(raw: Any) -> str:
    """Ask HN bodies are HTML; strip tags/entities so the digest stays readable."""
    if not isinstance(raw, str):
        return ""
    text = re.sub(r"<[^>]+>", " ", html.unescape(raw))
    text = re.sub(r"\s+", " ", text).strip()
    return text[:MAX_TEXT_CHARS]


def _story_item(hit: dict[str, Any]) -> dict[str, Any]:
    object_id = str(hit.get("objectID") or "")
    url = hit.get("url") or (f"https://news.ycombinator.com/item?id={object_id}" if object_id else "")
    points = hit.get("points")
    comments = hit.get("num_comments")
    return {
        "title": (hit.get("title") or "Untitled").strip(),
        "url": url,
        "source": domain(hit.get("url") or "") or "news.ycombinator.com",
        "summary": f"{points or 0} points · {comments or 0} comments",
        "points": points,
        "comments": comments,
        "created_at": hit.get("created_at"),
        "hn_url": f"https://news.ycombinator.com/item?id={object_id}" if object_id else "",
        "text": _plain_text(hit.get("story_text")),
    }


def hackernews_search(query: str = "", sort: str = "relevance", limit: int = 5) -> dict[str, Any]:
    try:
        text, normalized_sort, max_results = _clean_args(query, sort, limit)
        response = requests.get(
            SORT_ENDPOINTS[normalized_sort],
            params={"query": text, "tags": "story", "hitsPerPage": max_results},
            headers={"User-Agent": USER_AGENT, "Accept": "application/json"},
            timeout=TIMEOUT,
        )
        response.raise_for_status()
        data = response.json()
        items = [_story_item(hit) for hit in (data.get("hits") or []) if isinstance(hit, dict)]
        return {
            "tool": "hackernews_search",
            "query": text,
            "sort": normalized_sort,
            "items": items,
            "count": len(items),
            "total_hits": data.get("nbHits"),
            "freshness": "live_hn_index",
        }
    except Exception as exc:
        return err("hackernews_search", exc)
