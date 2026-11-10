"""TODO CP3 (student): Tool Unit Test Challenge.

Each test below is a stub. Replace `pytest.skip(...)` with a real test.
Patterns to copy are in test_tools_examples.py. Fixtures are in conftest.py.

Rules:
- Offline only: mock HTTP with `fake_http`, set fake keys with `monkeypatch.setenv`.
- One behaviour per test. Name the test after the behaviour, not the function.
- Done = `pytest tests/ -v` shows 0 skipped, 0 failed.
"""
from __future__ import annotations

import pytest

from conftest import FakeResponse  # noqa: F401  (you will need it)
from tools import TOOL_FUNCTIONS  # noqa: F401

TODO = "TODO CP3 (student): implement this test"


# ---------------- clarify ----------------

def test_clarify_choice_returns_options_and_awaits_user() -> None:
    # Call clarify with response_type="choice" and 2 options.
    # Assert: options are returned unchanged, awaiting_user is True.
    pytest.skip(TODO)


# ---------------- format ----------------

def test_format_sections_groups_items_by_section() -> None:
    # Items with section "A", "B", "A" -> markdown has exactly one "## A" and one "## B".
    pytest.skip(TODO)


def test_format_thread_numbers_items() -> None:
    # template="thread" -> lines start with "1/", "2/", ...
    pytest.skip(TODO)


def test_format_empty_items_does_not_crash() -> None:
    # items=None and items=[] -> item_count == 0, no exception.
    pytest.skip(TODO)


# ---------------- send (guardrail) ----------------

def test_send_confirmed_posts_to_telegram(monkeypatch, fake_http) -> None:
    # Set TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID, mock HTTP.
    # Assert: exactly one POST, URL contains the token, json has chat_id + text, status == "sent".
    pytest.skip(TODO)


def test_send_confirmed_without_env_returns_error_and_no_request(fake_http) -> None:
    pytest.skip(TODO)


# ---------------- lookup ----------------

def test_lookup_without_timeframe_omits_time_range(monkeypatch, fake_http) -> None:
    # timeframe=None -> request body has no "time_range" key.
    pytest.skip(TODO)


# ---------------- fetch ----------------

def test_fetch_maps_firecrawl_response(monkeypatch, fake_http) -> None:
    # Mock {"data": {"markdown": "...", "metadata": {"title": "T", "sourceURL": "https://..."}}}
    # Assert title/url/source/summary in result["items"][0].
    pytest.skip(TODO)


def test_fetch_truncates_markdown_to_4000_chars(monkeypatch, fake_http) -> None:
    pytest.skip(TODO)


# ---------------- timeline / social_search ----------------

def test_timeline_respects_limit_and_skips_items_without_id(monkeypatch, fake_http) -> None:
    # Mock {"timeline": [...]} with 1 item missing tweet_id and 6 valid items, limit=3.
    # Assert 3 items, and each url looks like https://x.com/<handle>/status/<id>.
    pytest.skip(TODO)


def test_social_search_passes_search_type(monkeypatch, fake_http) -> None:
    # Assert the request params carry the query and search_type ("Top" / "Latest").
    pytest.skip(TODO)


# ---------------- policy (local knowledge + trust boundary) ----------------

def test_policy_empty_query_returns_no_results() -> None:
    pytest.skip(TODO)


def test_policy_area_filter_only_returns_that_area() -> None:
    # policy_area="data_privacy" -> every result has policy_area == "data_privacy".
    pytest.skip(TODO)


def test_policy_instruction_like_lines_go_to_untrusted_text() -> None:
    # One policy file contains a quoted line that tries to give the assistant orders.
    # Query that section (source_citation) and assert: that line is in untrusted_text, NOT in facts.
    pytest.skip(TODO)


# ---------------- YOUR NEW TOOL(S) ----------------
# Write at least 3 tests per tool your team adds:
#   1. happy path (mocked if it calls an API)
#   2. bad / missing input from the model (empty string, wrong type, out-of-enum value)
#   3. failure path (missing key, HTTP error, timeout) -> returns error dict, does not raise

from datetime import date  # noqa: E402

import requests  # noqa: E402

from tools.top_papers.tool import _months_ago  # noqa: E402

OPENALEX_WORK = {
    "id": "https://openalex.org/W1",
    "doi": "https://doi.org/10.1000/xyz",
    "title": "A Survey of Agents",
    "publication_date": "2026-05-09",
    "cited_by_count": 812,
    "primary_location": {
        "landing_page_url": "https://example.org/paper",
        "source": {"display_name": "Nature", "type": "journal"},
    },
    "authorships": [{"author": {"display_name": f"Author {i}"}} for i in range(7)],
}


def test_top_papers_sends_date_venue_sort_filters_and_maps_results(fake_http) -> None:
    calls = fake_http(FakeResponse({"meta": {"count": 1234}, "results": [OPENALEX_WORK]}))

    result = TOOL_FUNCTIONS["top_papers"](query="AI agents", months=9, venue_type="all", limit=10)

    params = calls[0]["params"]
    from_date = _months_ago(date.today(), 9).isoformat()
    assert calls[0]["url"] == "https://api.openalex.org/works"
    assert params["search"] == "AI agents"
    assert params["sort"] == "cited_by_count:desc"
    assert params["per_page"] == 10
    assert f"from_publication_date:{from_date}" in params["filter"]
    assert f"to_publication_date:{date.today().isoformat()}" in params["filter"]
    assert "primary_location.source.type:journal|conference" in params["filter"]
    assert result["from_date"] == from_date
    assert result["total_matches"] == 1234
    item = result["items"][0]
    assert item["title"] == "A Survey of Agents"
    assert item["venue"] == "Nature" and item["venue_type"] == "journal"
    assert item["cited_by_count"] == 812
    assert item["url"] == "https://doi.org/10.1000/xyz"
    assert item["authors"] == [f"Author {i}" for i in range(5)]  # capped at 5


def test_top_papers_bad_input_from_model_is_normalised(fake_http) -> None:
    calls = fake_http(FakeResponse({"results": []}))

    result = TOOL_FUNCTIONS["top_papers"](
        query="   ", months="nine", venue_type="Workshop", limit=500, sort_by="hot", source="google",
    )

    params = calls[0]["params"]
    assert calls[0]["url"] == "https://api.openalex.org/works"  # unknown source -> openalex
    assert "search" not in params  # blank query -> no keyword filter
    assert params["per_page"] == 25  # limit clamped
    assert params["sort"] == "cited_by_count:desc"  # unknown sort -> citations
    assert result["months"] == 9  # non-numeric -> default
    assert result["venue_type"] == "all"  # out-of-enum -> all
    assert result["sort_by"] == "citations" and result["source"] == "openalex"
    assert "primary_location.source.type:journal|conference" in params["filter"]
    assert result["items"] == []


def test_top_papers_conference_only_filter_and_string_months(fake_http) -> None:
    calls = fake_http(FakeResponse({"results": []}))
    TOOL_FUNCTIONS["top_papers"](query="LLM", venue_type="conference", months="3")
    assert "primary_location.source.type:conference" in calls[0]["params"]["filter"]
    assert f"from_publication_date:{_months_ago(date.today(), 3).isoformat()}" in calls[0]["params"]["filter"]


def test_top_papers_http_error_returns_error_dict(fake_http) -> None:
    fake_http(FakeResponse(status_code=429))
    result = TOOL_FUNCTIONS["top_papers"](query="LLM")
    assert result["tool"] == "top_papers"
    assert result["error"] == "HTTPError"
    assert "429" in result["message"]


def test_top_papers_timeout_returns_error_dict(fake_http) -> None:
    fake_http(requests.Timeout("timed out"))
    result = TOOL_FUNCTIONS["top_papers"](query="LLM")
    assert result["error"] == "Timeout"


def test_top_papers_openalex_sort_options_map_to_api_sort(fake_http) -> None:
    calls = fake_http(FakeResponse({"results": []}))
    TOOL_FUNCTIONS["top_papers"](query="LLM", sort_by="relevance")
    TOOL_FUNCTIONS["top_papers"](query="LLM", sort_by="newest", limit="5", months=12)
    assert calls[0]["params"]["sort"] == "relevance_score:desc"
    assert calls[1]["params"]["sort"] == "publication_date:desc"
    assert calls[1]["params"]["per_page"] == 5
    assert f"from_publication_date:{_months_ago(date.today(), 12).isoformat()}" in calls[1]["params"]["filter"]


def test_top_papers_relevance_without_query_falls_back_to_citations(fake_http) -> None:
    calls = fake_http(FakeResponse({"results": []}))
    result = TOOL_FUNCTIONS["top_papers"](query="", sort_by="relevance")
    assert calls[0]["params"]["sort"] == "cited_by_count:desc"
    assert result["sort_by"] == "citations"
    assert "fell back" in result["note"]


S2_PAPER = {
    "paperId": "abc",
    "title": "Agents at Scale",
    "venue": "NeurIPS",
    "publicationDate": "2026-06-01",
    "citationCount": 321,
    "authors": [{"name": "Ann"}, {"name": "Bob"}],
    "externalIds": {"DOI": "10.5555/agents"},
    "url": "https://www.semanticscholar.org/paper/abc",
    "publicationTypes": ["Conference"],
}


def test_top_papers_semantic_scholar_citations_uses_bulk_sort_and_maps_results(fake_http) -> None:
    calls = fake_http(FakeResponse({"total": 77, "data": [S2_PAPER, S2_PAPER, S2_PAPER]}))

    result = TOOL_FUNCTIONS["top_papers"](query="AI agents", source="semantic_scholar", venue_type="conference", limit=2)

    params = calls[0]["params"]
    from_date = _months_ago(date.today(), 9).isoformat()
    assert calls[0]["url"] == "https://api.semanticscholar.org/graph/v1/paper/search/bulk"
    assert params["query"] == "AI agents"
    assert params["sort"] == "citationCount:desc"
    assert params["publicationTypes"] == "Conference"
    assert params["publicationDateOrYear"] == f"{from_date}:{date.today().isoformat()}"
    assert calls[0]["headers"] == {}  # no key -> no x-api-key header
    assert len(result["items"]) == 2  # bulk returns many rows, trimmed to limit
    assert result["total_matches"] == 77
    item = result["items"][0]
    assert item["venue"] == "NeurIPS" and item["venue_type"] == "conference"
    assert item["cited_by_count"] == 321
    assert item["url"] == "https://doi.org/10.5555/agents"
    assert item["source"] == "semanticscholar.org"


def test_top_papers_semantic_scholar_relevance_uses_search_endpoint_with_key(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("SEMANTIC_SCHOLAR_API_KEY", "s2-key")
    calls = fake_http(FakeResponse({"total": 1, "data": [S2_PAPER]}))

    TOOL_FUNCTIONS["top_papers"](query="LLM", source="semantic_scholar", sort_by="relevance", limit=7)

    assert calls[0]["url"] == "https://api.semanticscholar.org/graph/v1/paper/search"
    assert calls[0]["params"]["limit"] == 7
    assert "sort" not in calls[0]["params"]
    assert calls[0]["params"]["publicationTypes"] == "JournalArticle,Conference"
    assert calls[0]["headers"] == {"x-api-key": "s2-key"}


def test_top_papers_semantic_scholar_rate_limit_returns_error_dict(fake_http) -> None:
    fake_http(FakeResponse(status_code=429))
    result = TOOL_FUNCTIONS["top_papers"](query="LLM", source="semantic_scholar")
    assert result["tool"] == "top_papers"
    assert result["error"] == "HTTPError"


def test_months_ago_clamps_to_end_of_month() -> None:
    assert _months_ago(date(2026, 11, 30), 9) == date(2026, 2, 28)
    assert _months_ago(date(2026, 3, 15), 9) == date(2025, 6, 15)
