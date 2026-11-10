from __future__ import annotations

import html
import re
from typing import Any

import requests

from tools._shared import TIMEOUT, err

HN_SEARCH_URL = "https://hn.algolia.com/api/v1/search"
HN_SEARCH_BY_DATE_URL = "https://hn.algolia.com/api/v1/search_by_date"
ALLOWED_TAGS = {"story", "comment", "ask_hn", "show_hn", "all"}
ALLOWED_SORTS = {"relevance", "date"}


def _parse_limit(limit: Any, *, default: int = 5, max_limit: int = 20) -> int:
    """Validate and normalize the limit argument from model output."""
    if isinstance(limit, bool):
        raise ValueError("limit must be an integer, not bool")
    parsed = int(default if limit is None else limit)
    if parsed < 1:
        raise ValueError("limit must be >= 1")
    return min(parsed, max_limit)


def _clean_text(value: str | None) -> str:
    """Strip basic HTML markup from HN comment/story text."""
    if not value:
        return ""
    text = re.sub(r"<[^>]+>", " ", html.unescape(value))
    return " ".join(text.split())


def _format_hn_item(raw: dict[str, Any]) -> dict[str, Any]:
    """Normalize an Algolia HN hit into a standard research item."""
    object_id = str(raw.get("objectID") or "").strip()
    hn_url = f"https://news.ycombinator.com/item?id={object_id}" if object_id else ""
    external_url = str(raw.get("url") or "").strip()
    url = external_url or hn_url

    title = str(raw.get("title") or raw.get("story_title") or "").strip() or f"HN item {object_id}"
    author = str(raw.get("author") or "").strip()
    points = raw.get("points")
    num_comments = raw.get("num_comments")

    comment_excerpt = _clean_text(raw.get("comment_text") or raw.get("story_text"))
    if comment_excerpt:
        summary = comment_excerpt[:400]
    else:
        summary = (
            f"Points: {points if points is not None else 0} | "
            f"Comments: {num_comments if num_comments is not None else 0} | "
            f"By: {author or 'unknown'} | HN: {hn_url}"
        )

    return {
        "object_id": object_id,
        "title": title,
        "url": url,
        "hn_url": hn_url,
        "source": "news.ycombinator.com",
        "summary": summary,
        "author": author,
        "points": points,
        "num_comments": num_comments,
        "created_at": raw.get("created_at"),
    }


def search_hacker_news(
    query: str = "",
    tag: str = "story",
    sort_by: str = "relevance",
    limit: int = 5,
) -> dict[str, Any]:
    """Search stories and discussions on Hacker News via the Algolia API."""
    try:
        # Validate inputs before sending any HTTP request.
        if not isinstance(query, str):
            raise ValueError("query must be a string")
        cleaned_query = query.strip()
        if not cleaned_query:
            raise ValueError("query must not be empty")

        if not isinstance(tag, str) or tag not in ALLOWED_TAGS:
            raise ValueError(f"Invalid tag={tag!r}. Allowed: {sorted(ALLOWED_TAGS)}")

        if not isinstance(sort_by, str) or sort_by not in ALLOWED_SORTS:
            raise ValueError(f"Invalid sort_by={sort_by!r}. Allowed: {sorted(ALLOWED_SORTS)}")

        parsed_limit = _parse_limit(limit)

        endpoint = HN_SEARCH_BY_DATE_URL if sort_by == "date" else HN_SEARCH_URL
        params: dict[str, Any] = {
            "query": cleaned_query,
            "hitsPerPage": parsed_limit,
        }
        if tag != "all":
            params["tags"] = tag

        # Call requests.get directly so offline tests can intercept via fake_http.
        response = requests.get(endpoint, params=params, timeout=TIMEOUT)
        response.raise_for_status()

        data = response.json()
        if not isinstance(data, dict) or not isinstance(data.get("hits"), list):
            raise ValueError("Unexpected response format from Hacker News API: missing 'hits' list")

        items = [
            _format_hn_item(hit)
            for hit in data["hits"]
            if isinstance(hit, dict) and hit.get("objectID")
        ][:parsed_limit]

        return {
            "tool": "search_hacker_news",
            "query": cleaned_query,
            "tag": tag,
            "sort_by": sort_by,
            "items": items,
        }
    except Exception as exc:
        return err("search_hacker_news", exc)

