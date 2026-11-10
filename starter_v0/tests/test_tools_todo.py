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


# ---------------- NEW TOOL 1: date_calc ----------------
def test_date_calc_happy_path() -> None:
    tool = TOOL_FUNCTIONS["date_calc"]

    result = tool(
        op="diff_days",
        date1="2026-11-10",
        date2="2027-01-01",
    )

    assert result == {"result": 52}


def test_date_calc_bad_input_from_model() -> None:
    tool = TOOL_FUNCTIONS["date_calc"]

    result = tool(
        op="diff_days",
        date1="abc",
        date2="2027-01-01",
    )

    assert isinstance(result, dict)
    assert "error" in result


def test_date_calc_failure_returns_error_dict() -> None:
    tool = TOOL_FUNCTIONS["date_calc"]

    result = tool(
        op="add_days",
        date1="9999-12-31",
        days=1,
    )

    assert isinstance(result, dict)
    assert "error" in result
    
# ---------------- NEW TOOL 2: cite format ----------------
def test_cite_format_single_author_with_url():
    tool = TOOL_FUNCTIONS["cite_format"]

    result = tool(
        title="Deep Learning Basics",
        authors=["Nguyen, An"],
        year=2024,
        url="https://example.com/dl"
    )

    assert result == {
        "citation": "Nguyen, A. (2024). Deep Learning Basics. https://example.com/dl"
    }


def test_cite_format_two_authors_without_url():
    tool = TOOL_FUNCTIONS["cite_format"]

    result = tool(
        title="Intro to NLP",
        authors=["Smith, John", "Lee, Kim"],
        year=2020
    )

    assert result == {
        "citation": "Smith, J., & Lee, K. (2020). Intro to NLP."
    }


def test_cite_format_missing_year():
    tool = TOOL_FUNCTIONS["cite_format"]

    result = tool(
        title="Draft Notes",
        authors=["Tran, Binh"],
        year=None
    )

    assert "(n.d.)" in result["citation"]


def test_cite_format_missing_required_fields():
    tool = TOOL_FUNCTIONS["cite_format"]

    empty_title = tool(title="", authors=["Nguyen, An"])
    empty_authors = tool(title="Draft Notes", authors=[])

    assert "error" in empty_title
    assert "error" in empty_authors


def test_cite_format_unsupported_style():
    tool = TOOL_FUNCTIONS["cite_format"]

    result = tool(
        title="Draft Notes",
        authors=["Tran, Binh"],
        style="mla"
    )

    assert "error" in result
    assert "style" in result["error"].lower()