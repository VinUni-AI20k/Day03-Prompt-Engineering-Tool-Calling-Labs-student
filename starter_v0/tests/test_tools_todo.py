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
# text_stats, date_diff, dedupe: local tools, no API, so no fake_http needed.

text_stats_tool = TOOL_FUNCTIONS["text_stats"]
date_diff_tool = TOOL_FUNCTIONS["date_diff"]
dedupe_tool = TOOL_FUNCTIONS["dedupe"]


# ---- text_stats ----

def test_text_stats_counts_words_sentences_and_reading_time() -> None:
    result = text_stats_tool(text="Xin chào các bạn. Hôm nay trời đẹp! Bạn khỏe không?")
    assert result["words"] == 11
    assert result["sentences"] == 3
    assert result["chars"] == len("Xin chào các bạn. Hôm nay trời đẹp! Bạn khỏe không?")
    assert result["reading_minutes"] == 1


def test_text_stats_empty_or_none_text_returns_zeros() -> None:
    for value in ("", None):
        result = text_stats_tool(text=value)
        assert (result["chars"], result["words"], result["sentences"], result["reading_minutes"]) == (0, 0, 0, 0)


def test_text_stats_wrong_type_returns_error_dict() -> None:
    result = text_stats_tool(text=12345)
    assert result["error"] == "TypeError"
    assert result["tool"] == "text_stats"


# ---- date_diff ----

def test_date_diff_returns_days_and_weeks() -> None:
    result = date_diff_tool(start_date="2026-11-01", end_date="2026-11-15")
    assert result["days"] == 14
    assert result["weeks"] == 2.0


def test_date_diff_end_before_start_gives_negative_days() -> None:
    assert date_diff_tool(start_date="2026-11-15", end_date="2026-11-01")["days"] == -14


def test_date_diff_bad_or_missing_date_returns_error_dict() -> None:
    for start, end in (("", "2026-11-15"), ("10/11/2026", "2026-11-15"), ("2026-02-30", "2026-03-01")):
        result = date_diff_tool(start_date=start, end_date=end)
        assert result["error"] == "ValueError"


# ---- dedupe ----

def test_dedupe_removes_duplicate_urls_and_keeps_first() -> None:
    items = [
        {"title": "A", "url": "https://www.Example.com/post/"},
        {"title": "A copy", "url": "https://example.com/post"},
        {"title": "B", "url": "https://example.com/other"},
    ]
    result = dedupe_tool(items=items)
    assert [item["title"] for item in result["items"]] == ["A", "B"]
    assert result["item_count"] == 2
    assert result["removed_count"] == 1


def test_dedupe_empty_items_and_items_without_key_do_not_crash() -> None:
    assert dedupe_tool(items=None)["item_count"] == 0
    assert dedupe_tool(items=[])["removed_count"] == 0
    items = [{"title": "No link 1"}, {"title": "No link 2"}, "not a dict"]
    result = dedupe_tool(items=items)
    assert result["item_count"] == 3
    assert result["removed_count"] == 0


def test_dedupe_unknown_key_returns_error_dict() -> None:
    result = dedupe_tool(items=[{"url": "https://a.com"}], key="author")
    assert result["error"] == "ValueError"
    assert "key must be one of" in result["message"]
