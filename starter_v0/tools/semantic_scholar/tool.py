from __future__ import annotations

import os
import time
from typing import Any

import requests

from tools._shared import TIMEOUT, err


SEMANTIC_SCHOLAR_API_URL = "https://api.semanticscholar.org/graph/v1/paper/search"
SEMANTIC_SCHOLAR_MIN_INTERVAL_SECONDS = 1.0
_last_semantic_scholar_request_at = 0.0

PAPER_FIELDS = ",".join(
    [
        "title",
        "abstract",
        "year",
        "publicationDate",
        "authors",
        "venue",
        "citationCount",
        "referenceCount",
        "url",
        "openAccessPdf",
        "externalIds",
        "fieldsOfStudy",
        "publicationTypes",
    ]
)


def _semantic_scholar_headers() -> dict[str, str]:
    headers = {"User-Agent": "AI20k-Day03-Research-Agent/1.0"}
    api_key = os.getenv("SEMANTIC_SCHOLAR_API_KEY", "").strip()
    if api_key:
        headers["x-api-key"] = api_key
    return headers


def _rate_limit_semantic_scholar() -> None:
    global _last_semantic_scholar_request_at

    elapsed = time.monotonic() - _last_semantic_scholar_request_at
    if elapsed < SEMANTIC_SCHOLAR_MIN_INTERVAL_SECONDS:
        time.sleep(SEMANTIC_SCHOLAR_MIN_INTERVAL_SECONDS - elapsed)
    _last_semantic_scholar_request_at = time.monotonic()


def _semantic_scholar_get(
    url: str, *, params: dict[str, Any] | None = None
) -> requests.Response:
    last_response: requests.Response | None = None

    for attempt in range(3):
        _rate_limit_semantic_scholar()
        response = requests.get(
            url,
            params=params,
            headers=_semantic_scholar_headers(),
            timeout=TIMEOUT,
        )
        last_response = response

        if response.status_code not in {429, 500, 502, 503, 504}:
            return response

        if attempt < 2:
            retry_after = response.headers.get("Retry-After")
            try:
                delay = float(retry_after) if retry_after else 2 ** (attempt + 1)
            except ValueError:
                delay = 2 ** (attempt + 1)
            time.sleep(min(delay, 30.0))

    assert last_response is not None
    return last_response


def _normalize_paper(paper: dict[str, Any]) -> dict[str, Any]:
    authors = paper.get("authors") or []
    open_access_pdf = paper.get("openAccessPdf") or {}
    external_ids = paper.get("externalIds") or {}

    return {
        "paper_id": paper.get("paperId"),
        "title": paper.get("title") or "",
        "abstract": paper.get("abstract") or "",
        "authors": [
            author.get("name", "")
            for author in authors
            if isinstance(author, dict) and author.get("name")
        ],
        "year": paper.get("year"),
        "published": paper.get("publicationDate"),
        "venue": paper.get("venue"),
        "citation_count": paper.get("citationCount"),
        "reference_count": paper.get("referenceCount"),
        "url": paper.get("url"),
        "pdf_url": open_access_pdf.get("url"),
        "is_open_access": bool(open_access_pdf.get("url")),
        "doi": external_ids.get("DOI"),
        "arxiv_id": external_ids.get("ArXiv"),
        "fields_of_study": [
            item.get("category")
            for item in (paper.get("fieldsOfStudy") or [])
            if isinstance(item, dict) and item.get("category")
        ],
        "publication_types": paper.get("publicationTypes") or [],
        "source": "semanticscholar.org",
    }


def semantic_scholar_search(
    query: str = "",
    max_results: int = 5,
    sort_by: str = "relevance",
) -> dict[str, Any]:
    """Search scholarly papers using the Semantic Scholar Academic Graph API."""
    try:
        cleaned_query = " ".join((query or "").split())
        if not cleaned_query:
            raise ValueError("query must not be empty")

        max_results = max(1, min(int(max_results or 5), 100))
        sort_by = (
            sort_by
            if sort_by in {"relevance", "citationCount", "publicationDate"}
            else "relevance"
        )

        params: dict[str, Any] = {
            "query": cleaned_query,
            "limit": max_results,
            "fields": PAPER_FIELDS,
        }
        if sort_by != "relevance":
            params["sort"] = f"{sort_by}:desc"

        response = _semantic_scholar_get(
            SEMANTIC_SCHOLAR_API_URL,
            params=params,
        )
        response.raise_for_status()
        payload = response.json()

        items = [
            _normalize_paper(item)
            for item in (payload.get("data") or [])
            if isinstance(item, dict)
        ]

        return {
            "tool": "semantic_scholar_search",
            "query": cleaned_query,
            "sort_by": sort_by,
            "total_results": payload.get("total"),
            "items": items,
            "rate_limit_note": (
                "Requests are spaced by at least 1 second in-process. "
                "The API may impose stricter limits; an optional API key can "
                "be supplied through SEMANTIC_SCHOLAR_API_KEY."
            ),
        }
    except Exception as exc:
        return err("semantic_scholar_search", exc)
