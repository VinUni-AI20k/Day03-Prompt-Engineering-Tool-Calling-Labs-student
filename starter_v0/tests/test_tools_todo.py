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

deduplicate_tool = TOOL_FUNCTIONS["deduplicate_sources"]


def _source_audit_tool():
    tool = TOOL_FUNCTIONS.get("source_audit")
    assert callable(tool), "source_audit is not registered"
    return tool

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

def test_deduplicate_sources_keeps_first_duplicate_and_order() -> None:
    first = {"title": "First", "url": "https://example.com/a"}
    duplicate = {"title": "Duplicate", "url": "https://example.com/a"}
    second = {"title": "Second", "url": "https://example.com/b"}

    result = deduplicate_tool(items=[first, duplicate, second])

    assert result["items"] == [first, second]
    assert result["removed_count"] == 1


def test_deduplicate_sources_normalizes_trailing_slash() -> None:
    canonical = {"title": "First", "url": "https://openai.com/blog/gpt-5"}
    duplicate = {"title": "Duplicate", "url": "https://openai.com/blog/gpt-5/"}

    result = deduplicate_tool(items=[canonical, duplicate])

    assert result["items"] == [canonical]
    assert result["removed_count"] == 1


def test_deduplicate_sources_keeps_items_without_url() -> None:
    no_url = {"title": "No URL"}
    empty_url = {"title": "Empty URL", "url": ""}

    result = deduplicate_tool(items=[no_url, empty_url])

    assert result["items"] == [no_url, empty_url]
    assert result["removed_count"] == 0


def test_deduplicate_sources_invalid_items_returns_error_dict() -> None:
    result = deduplicate_tool(items="not-a-list")

    assert result["error"] == "TypeError"
    assert "items must be a list" in result["message"]
def test_source_audit_accepts_complete_http_citations() -> None:
    result = _source_audit_tool()(items=[{
        "title": "Research report",
        "url": "https://example.org/report",
        "source": "Example",
        "summary": "A short summary.",
    }])

    assert result == {
        "tool": "source_audit",
        "checked_count": 1,
        "valid_count": 1,
        "ok": True,
        "issues": [],
    }


def test_source_audit_reports_missing_title_and_invalid_url() -> None:
    result = _source_audit_tool()(items=[
        {"url": "https://example.org/no-title"},
        {"title": "FTP source", "url": "ftp://example.org/report"},
    ])

    assert result["ok"] is False
    assert result["checked_count"] == 2
    assert result["valid_count"] == 0
    assert result["issues"] == [
        {"index": 0, "title": None, "problems": ["missing_title"]},
        {"index": 1, "title": "FTP source", "problems": ["invalid_url"]},
    ]


def test_source_audit_rejects_non_numeric_url_port() -> None:
    result = _source_audit_tool()(items=[
        {"title": "Bad port", "url": "https://example.org:abc/report"},
    ])

    assert result["ok"] is False
    assert result["valid_count"] == 0
    assert result["issues"] == [
        {"index": 0, "title": "Bad port", "problems": ["invalid_url"]},
    ]


def test_source_audit_wrong_items_type_returns_error_dict() -> None:
    result = _source_audit_tool()(items="not a list")

    assert result == {
        "tool": "source_audit",
        "error": "TypeError",
        "message": "items must be a list of objects",
    }
