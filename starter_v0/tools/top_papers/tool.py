from __future__ import annotations

import calendar
import os
from datetime import date
from typing import Any

import requests

from tools._shared import TIMEOUT, err


OPENALEX_WORKS_URL = "https://api.openalex.org/works"
S2_SEARCH_URL = "https://api.semanticscholar.org/graph/v1/paper/search"
S2_BULK_URL = "https://api.semanticscholar.org/graph/v1/paper/search/bulk"

VENUE_TYPES = {"all", "journal", "conference"}
SORT_OPTIONS = {"citations", "relevance", "newest"}
SOURCES = {"openalex", "semantic_scholar"}
MAX_MONTHS = 24
MAX_LIMIT = 25

OPENALEX_SELECT = "id,doi,title,publication_date,cited_by_count,primary_location,authorships"
OPENALEX_SORT = {
    "citations": "cited_by_count:desc",
    "relevance": "relevance_score:desc",
    "newest": "publication_date:desc",
}

S2_FIELDS = "title,venue,publicationDate,citationCount,authors,externalIds,url,publicationTypes"
S2_SORT = {"citations": "citationCount:desc", "newest": "publicationDate:desc"}
S2_VENUE = {"journal": "JournalArticle", "conference": "Conference"}


def _months_ago(today: date, months: int) -> date:
    """Same day-of-month `months` months back, clamped to the last day of that month."""
    total = today.year * 12 + (today.month - 1) - months
    year, month = divmod(total, 12)
    month += 1
    day = min(today.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


def _to_int(value: Any, default: int, low: int, high: int) -> int:
    try:
        number = int(value)
    except (TypeError, ValueError):
        return default
    return max(low, min(number, high))


def _choice(value: Any, allowed: set[str], default: str) -> str:
    text = str(value or default).strip().lower()
    return text if text in allowed else default


def _item(*, title: str, authors: list[str], venue: str, venue_type: str, published: str,
          citations: int, doi: str | None, url: str, source: str) -> dict[str, Any]:
    return {
        "title": title,
        "authors": authors[:5],
        "venue": venue,
        "venue_type": venue_type,
        "publication_date": published,
        "cited_by_count": citations,
        "doi": doi,
        "url": url,
        "source": source,
        # `summary` lets the result be passed straight into the `format` tool.
        "summary": f"{title} ({venue}, {published}) - {citations} citations",
    }


# ---------------- OpenAlex ----------------

def _openalex(query: str, from_date: date, today: date, venue_type: str, limit: int, sort_by: str) -> tuple[list[dict[str, Any]], int | None]:
    source_filter = "journal|conference" if venue_type == "all" else venue_type
    params: dict[str, Any] = {
        "filter": ",".join([
            f"from_publication_date:{from_date.isoformat()}",
            f"to_publication_date:{today.isoformat()}",
            f"primary_location.source.type:{source_filter}",
        ]),
        "sort": OPENALEX_SORT[sort_by],
        "per_page": limit,
        "select": OPENALEX_SELECT,
    }
    if query:
        params["search"] = query
    api_key = os.getenv("OPENALEX_API_KEY")
    if api_key:
        params["api_key"] = api_key

    response = requests.get(OPENALEX_WORKS_URL, params=params, timeout=TIMEOUT)
    response.raise_for_status()
    data = response.json()
    items = []
    for work in (data.get("results") or [])[:limit]:
        location = work.get("primary_location") or {}
        src = location.get("source") or {}
        authors = [(a.get("author") or {}).get("display_name") for a in (work.get("authorships") or [])]
        items.append(_item(
            title=work.get("title") or "",
            authors=[name for name in authors if name],
            venue=src.get("display_name") or "",
            venue_type=src.get("type") or "",
            published=work.get("publication_date") or "",
            citations=work.get("cited_by_count") or 0,
            doi=work.get("doi"),
            url=work.get("doi") or location.get("landing_page_url") or work.get("id") or "",
            source="openalex.org",
        ))
    return items, (data.get("meta") or {}).get("count")


# ---------------- Semantic Scholar ----------------

def _s2_venue_type(types: list[str] | None) -> str:
    types = types or []
    if "Conference" in types:
        return "conference"
    if "JournalArticle" in types:
        return "journal"
    return ""


def _semantic_scholar(query: str, from_date: date, today: date, venue_type: str, limit: int, sort_by: str) -> tuple[list[dict[str, Any]], int | None]:
    params: dict[str, Any] = {
        "publicationDateOrYear": f"{from_date.isoformat()}:{today.isoformat()}",
        "publicationTypes": "JournalArticle,Conference" if venue_type == "all" else S2_VENUE[venue_type],
        "fields": S2_FIELDS,
    }
    if query:
        params["query"] = query
    if sort_by == "relevance":
        # Relevance ranking only exists on /paper/search (which does not take `sort`).
        url = S2_SEARCH_URL
        params["limit"] = limit
    else:
        # /paper/search/bulk supports `sort` but returns up to 1000 rows; we trim to `limit`.
        url = S2_BULK_URL
        params["sort"] = S2_SORT[sort_by]
    headers = {}
    api_key = os.getenv("SEMANTIC_SCHOLAR_API_KEY")
    if api_key:
        headers["x-api-key"] = api_key

    response = requests.get(url, params=params, headers=headers, timeout=TIMEOUT)
    response.raise_for_status()
    data = response.json()
    items = []
    for paper in (data.get("data") or [])[:limit]:
        doi = (paper.get("externalIds") or {}).get("DOI")
        doi_url = f"https://doi.org/{doi}" if doi else None
        items.append(_item(
            title=paper.get("title") or "",
            authors=[a.get("name") for a in (paper.get("authors") or []) if a.get("name")],
            venue=paper.get("venue") or "",
            venue_type=_s2_venue_type(paper.get("publicationTypes")),
            published=paper.get("publicationDate") or "",
            citations=paper.get("citationCount") or 0,
            doi=doi_url,
            url=doi_url or paper.get("url") or "",
            source="semanticscholar.org",
        ))
    return items, data.get("total")


# ---------------- Tool entry point ----------------

def get_top_papers(
    query: str = "",
    months: int = 9,
    venue_type: str = "all",
    limit: int = 10,
    sort_by: str = "citations",
    source: str = "openalex",
) -> dict[str, Any]:
    """Top papers published in journals/conferences within the last `months` months."""
    try:
        query = " ".join(str(query or "").split())
        months = _to_int(months, default=9, low=1, high=MAX_MONTHS)
        limit = _to_int(limit, default=10, low=1, high=MAX_LIMIT)
        venue_type = _choice(venue_type, VENUE_TYPES, "all")
        sort_by = _choice(sort_by, SORT_OPTIONS, "citations")
        source = _choice(source, SOURCES, "openalex")
        notes: list[str] = []
        if sort_by == "relevance" and not query:
            sort_by = "citations"
            notes.append("sort_by=relevance needs a query; fell back to citations.")

        today = date.today()
        from_date = _months_ago(today, months)
        fetch = _semantic_scholar if source == "semantic_scholar" else _openalex
        items, total = fetch(query, from_date, today, venue_type, limit, sort_by)
        if sort_by == "citations":
            notes.append("Recent papers have few citations, so counts are indicative only.")
        return {
            "tool": "top_papers",
            "query": query,
            "months": months,
            "venue_type": venue_type,
            "limit": limit,
            "sort_by": sort_by,
            "source": source,
            "from_date": from_date.isoformat(),
            "to_date": today.isoformat(),
            "total_matches": total,
            "items": items,
            "note": " ".join(notes),
        }
    except Exception as exc:
        return err("top_papers", exc)
