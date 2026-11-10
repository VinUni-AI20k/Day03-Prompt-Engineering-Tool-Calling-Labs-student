from __future__ import annotations

import os
from typing import Any

import requests

from tools._shared import TIMEOUT, err


OPENALEX_API_URL = "https://api.openalex.org/works"
OPENALEX_FIELDS = ",".join(
    [
        "id",
        "doi",
        "title",
        "publication_year",
        "publication_date",
        "authorships",
        "primary_location",
        "best_oa_location",
        "open_access",
        "cited_by_count",
        "type",
        "abstract_inverted_index",
        "ids",
    ]
)


def _openalex_params(
    query: str,
    max_results: int,
    sort_by: str,
) -> dict[str, Any]:
    params: dict[str, Any] = {
        "search": query,
        "per_page": max_results,
        "select": OPENALEX_FIELDS,
        "sort": {
            "relevance": "relevance_score:desc",
            "publication_date": "publication_date:desc",
            "cited_by_count": "cited_by_count:desc",
        }[sort_by],
    }

    api_key = os.getenv("OPENALEX_API_KEY", "").strip()
    if api_key:
        params["api_key"] = api_key

    mailto = os.getenv("OPENALEX_MAILTO", "").strip()
    if mailto:
        params["mailto"] = mailto

    return params


def _reconstruct_abstract(inverted_index: dict[str, list[int]] | None) -> str:
    """Reconstruct an abstract from OpenAlex's abstract inverted index."""
    if not isinstance(inverted_index, dict) or not inverted_index:
        return ""

    positioned_words: list[tuple[int, str]] = []
    for word, positions in inverted_index.items():
        if not isinstance(positions, list):
            continue
        for position in positions:
            if isinstance(position, int):
                positioned_words.append((position, word))

    positioned_words.sort(key=lambda item: item[0])
    return " ".join(word for _, word in positioned_words)


def _normalize_work(work: dict[str, Any]) -> dict[str, Any]:
    authorships = work.get("authorships") or []
    authors: list[str] = []

    for authorship in authorships:
        if not isinstance(authorship, dict):
            continue
        author = authorship.get("author") or {}
        name = author.get("display_name") if isinstance(author, dict) else None
        if name:
            authors.append(name)

    primary_location = work.get("primary_location") or {}
    primary_source = (
        primary_location.get("source") or {}
        if isinstance(primary_location, dict)
        else {}
    )
    best_oa_location = work.get("best_oa_location") or {}
    open_access = work.get("open_access") or {}
    ids = work.get("ids") or {}

    doi = work.get("doi") or ids.get("doi")
    if isinstance(doi, str) and doi.startswith("https://doi.org/"):
        doi = doi.removeprefix("https://doi.org/")

    return {
        "openalex_id": work.get("id"),
        "title": work.get("title") or "",
        "abstract": _reconstruct_abstract(work.get("abstract_inverted_index")),
        "authors": authors,
        "year": work.get("publication_year"),
        "published": work.get("publication_date"),
        "venue": (
            primary_source.get("display_name")
            if isinstance(primary_source, dict)
            else None
        ),
        "citation_count": work.get("cited_by_count"),
        "type": work.get("type"),
        "doi": doi,
        "url": work.get("id"),
        "landing_page_url": (
            best_oa_location.get("landing_page_url")
            if isinstance(best_oa_location, dict)
            else None
        ),
        "pdf_url": (
            best_oa_location.get("pdf_url")
            if isinstance(best_oa_location, dict)
            else None
        ),
        "is_open_access": bool(open_access.get("is_oa")),
        "source": "openalex.org",
    }


def openalex_search(
    query: str = "",
    max_results: int = 5,
    sort_by: str = "relevance",
) -> dict[str, Any]:
    """Search scholarly works using the official OpenAlex API."""
    try:
        cleaned_query = " ".join((query or "").split())
        if not cleaned_query:
            raise ValueError("query must not be empty")

        max_results = max(1, min(int(max_results or 5), 100))
        sort_by = (
            sort_by
            if sort_by in {"relevance", "publication_date", "cited_by_count"}
            else "relevance"
        )

        params = _openalex_params(cleaned_query, max_results, sort_by)
        response = requests.get(
            OPENALEX_API_URL,
            params=params,
            headers={"User-Agent": "AI20k-Day03-Research-Agent/1.0"},
            timeout=TIMEOUT,
        )
        response.raise_for_status()
        payload = response.json()

        meta = payload.get("meta") or {}
        items = [
            _normalize_work(item)
            for item in (payload.get("results") or [])
            if isinstance(item, dict)
        ]

        return {
            "tool": "openalex_search",
            "query": cleaned_query,
            "sort_by": sort_by,
            "total_results": meta.get("count"),
            "items": items,
        }
    except Exception as exc:
        return err("openalex_search", exc)
