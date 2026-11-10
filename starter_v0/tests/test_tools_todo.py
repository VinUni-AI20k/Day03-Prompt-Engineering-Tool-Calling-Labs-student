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

def test_github_search_happy_path_maps_results_and_request(fake_http) -> None:
    calls = fake_http(FakeResponse({
        "total_count": 1,
        "items": [{
            "full_name": "example/research-agent",
            "html_url": "https://github.com/example/research-agent",
            "description": "A research agent",
            "language": "Python",
            "stargazers_count": 42,
            "forks_count": 7,
            "updated_at": "2026-11-01T00:00:00Z",
        }],
    }))

    result = TOOL_FUNCTIONS["github_search"](
        query="research agent", language="Python", sort="stars", limit=3
    )

    assert calls[0]["url"] == "https://api.github.com/search/repositories"
    assert calls[0]["params"] == {
        "q": "research agent language:Python", "per_page": 3, "sort": "stars", "order": "desc"
    }
    assert result["total_count"] == 1
    assert result["items"][0] == {
        "name": "example/research-agent",
        "title": "example/research-agent",
        "url": "https://github.com/example/research-agent",
        "source": "github.com",
        "summary": "A research agent",
        "language": "Python",
        "stars": 42,
        "forks": 7,
        "updated_at": "2026-11-01T00:00:00Z",
    }


@pytest.mark.parametrize("bad_query", ["", "   ", None, 123])
def test_github_search_bad_query_returns_error_without_network(bad_query, fake_http) -> None:
    calls = fake_http(FakeResponse({"items": []}))

    result = TOOL_FUNCTIONS["github_search"](query=bad_query)

    assert result["error"] == "ValueError"
    assert "non-empty string" in result["message"]
    assert calls == []


def test_github_search_http_failure_returns_error_dict(fake_http) -> None:
    fake_http(FakeResponse(status_code=503))

    result = TOOL_FUNCTIONS["github_search"](query="research agent")

    assert result["tool"] == "github_search"
    assert result["error"] == "HTTPError"
    assert "HTTP 503" in result["message"]


# ---------------- deduplicate_sources ----------------

def test_deduplicate_sources_removes_canonical_url_duplicates() -> None:
    items = [
        {"title": "First", "url": "https://example.com/article/?utm_source=newsletter#section"},
        {"title": "Repeated", "url": "https://EXAMPLE.com/article"},
        {"title": "Other", "url": "https://example.com/other"},
    ]

    result = TOOL_FUNCTIONS["deduplicate_sources"](items=items, strategy="url")

    assert result["input_count"] == 3
    assert result["unique_count"] == 2
    assert result["duplicate_count"] == 1
    assert result["items"] == [items[0], items[2]]
    assert result["duplicates"][0]["reason"] == "url"


def test_deduplicate_sources_rejects_unknown_strategy() -> None:
    result = TOOL_FUNCTIONS["deduplicate_sources"](items=[], strategy="semantic")

    assert result["tool"] == "deduplicate_sources"
    assert result["error"] == "ValueError"
    assert "strategy" in result["message"]


def test_deduplicate_sources_malformed_item_returns_error_dict() -> None:
    result = TOOL_FUNCTIONS["deduplicate_sources"](items=[{"title": "Valid"}, "not-an-object"])

    assert result["error"] == "ValueError"
    assert "items[1]" in result["message"]


# ---------------- compare_sources ----------------

def test_compare_sources_builds_side_by_side_field_analysis() -> None:
    sources = [
        {"title": "Report", "source": "A", "published": "2026-11-01"},
        {"title": "Report", "source": "B", "published": "2026-11-02"},
    ]

    result = TOOL_FUNCTIONS["compare_sources"](
        sources=sources, fields=["title", "source", "published"]
    )

    assert result["source_count"] == 2
    assert result["comparisons"][0]["completeness"] == 1.0
    analyses = {item["field"]: item for item in result["field_analysis"]}
    assert analyses["title"]["all_equal"] is True
    assert analyses["published"]["all_equal"] is False


def test_compare_sources_requires_at_least_two_sources() -> None:
    result = TOOL_FUNCTIONS["compare_sources"](sources=[{"title": "Only one"}])

    assert result["tool"] == "compare_sources"
    assert result["error"] == "ValueError"
    assert "at least 2" in result["message"]


def test_compare_sources_malformed_source_returns_error_dict() -> None:
    result = TOOL_FUNCTIONS["compare_sources"](sources=[{"title": "Valid"}, None])

    assert result["error"] == "ValueError"
    assert "every source" in result["message"]


# ---------------- filter_by_date ----------------

def test_filter_by_date_uses_inclusive_boundaries_and_reports_exclusions() -> None:
    items = [
        {"title": "Before", "published": "2026-10-31"},
        {"title": "Start", "published": "2026-11-01"},
        {"title": "End", "published": "2026-11-10T23:00:00Z"},
        {"title": "Undated"},
    ]

    result = TOOL_FUNCTIONS["filter_by_date"](
        items=items, start_date="2026-11-01", end_date="2026-11-10"
    )

    assert [item["title"] for item in result["items"]] == ["Start", "End"]
    assert result["matched_count"] == 2
    assert [item["reason"] for item in result["excluded"]] == ["before_start", "missing_date"]


def test_filter_by_date_rejects_reversed_range() -> None:
    result = TOOL_FUNCTIONS["filter_by_date"](
        items=[], start_date="2026-11-10", end_date="2026-11-01"
    )

    assert result["tool"] == "filter_by_date"
    assert result["error"] == "ValueError"
    assert "must not be after" in result["message"]


def test_filter_by_date_malformed_item_returns_error_dict() -> None:
    result = TOOL_FUNCTIONS["filter_by_date"](
        items=["not-an-object"], start_date="2026-11-01"
    )

    assert result["error"] == "ValueError"
    assert "items[0]" in result["message"]
