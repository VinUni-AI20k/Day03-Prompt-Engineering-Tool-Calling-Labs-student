"""TODO(student): Tool Unit Test Challenge.

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

TODO = "TODO(student): implement this test"


# ---------------- clarify ----------------

def test_clarify_choice_returns_options_and_awaits_user() -> None:
    # Call clarify with response_type="choice" and 2 options.
    # Assert: options are returned unchanged, awaiting_user is True.
    pytest.skip(TODO)


# ---------------- format ----------------

def test_format_sections_groups_items_by_section() -> None:
    # Items with section "A", "B", "A" -> markdown has exactly one "## A" and one "## B".
    items = [
        {"title": "Item A1", "section": "A", "url": "https://a.com/1"},
        {"title": "Item B1", "section": "B", "url": "https://b.com/1"},
        {"title": "Item A2", "section": "A", "url": "https://a.com/2"},
    ]
    result = TOOL_FUNCTIONS["format"](items=items, template="sections")
    markdown = result["markdown"]
    assert markdown.count("## A") == 1
    assert markdown.count("## B") == 1
    assert "Item A1" in markdown
    assert "Item B1" in markdown
    assert "Item A2" in markdown


def test_format_thread_numbers_items() -> None:
    # template="thread" -> lines start with "1/", "2/", ...
    items = [
        {"title": "First tweet", "url": "https://x.com/1"},
        {"title": "Second tweet", "url": "https://x.com/2"},
    ]
    result = TOOL_FUNCTIONS["format"](items=items, template="thread")
    markdown = result["markdown"]
    assert "1/ First tweet" in markdown
    assert "2/ Second tweet" in markdown


def test_format_empty_items_does_not_crash() -> None:
    # items=None and items=[] -> item_count == 0, no exception.
    result_none = TOOL_FUNCTIONS["format"](items=None)
    assert result_none["item_count"] == 0
    assert result_none["markdown"] == ""

    result_empty = TOOL_FUNCTIONS["format"](items=[])
    assert result_empty["item_count"] == 0
    assert result_empty["markdown"] == ""


# ---------------- send (guardrail) ----------------

def test_send_confirmed_posts_to_telegram(monkeypatch, fake_http) -> None:
    # Set TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID, mock HTTP.
    # Assert: exactly one POST, URL contains the token, json has chat_id + text, status == "sent".
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "fake_bot_token")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "-100123456789")
    calls = fake_http(FakeResponse({"ok": True, "result": {"message_id": 123}}))
    result = TOOL_FUNCTIONS["send"](text="Bản tin công nghệ", confirmed=True)

    assert len(calls) == 1
    assert "fake_bot_token" in calls[0]["url"]
    assert calls[0]["json"]["chat_id"] == "-100123456789"
    assert calls[0]["json"]["text"] == "Bản tin công nghệ"
    assert result["status"] == "sent"


def test_send_confirmed_without_env_returns_error_and_no_request(fake_http) -> None:
    calls = fake_http(FakeResponse({"ok": True}))
    result = TOOL_FUNCTIONS["send"](text="Bản tin công nghệ", confirmed=True)

    assert len(calls) == 0
    assert result["error"] == "RuntimeError"
    assert "Missing TELEGRAM_BOT_TOKEN" in result["message"]


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

def test_my_new_tool_happy_path() -> None:
    result = TOOL_FUNCTIONS["sentiment_analyzer"](text="This breakthrough AI model is fantastic, innovative, and great!")
    assert result["status"] == "ok"
    assert result["sentiment"] == "positive"
    assert result["score"] > 0
    assert "fantastic" in result["details"]["positive_keywords"]


def test_my_new_tool_bad_input_from_model() -> None:
    # Empty string
    r1 = TOOL_FUNCTIONS["sentiment_analyzer"](text="")
    assert r1["status"] == "ok"
    assert r1["sentiment"] == "neutral"
    assert r1["score"] == 0.0

    # None or non-string
    r2 = TOOL_FUNCTIONS["sentiment_analyzer"](text=None)
    assert r2["status"] == "ok"
    assert r2["sentiment"] == "neutral"


def test_my_new_tool_failure_returns_error_dict() -> None:
    # Test negative sentiment and neutral sentiment
    neg = TOOL_FUNCTIONS["sentiment_analyzer"](text="The system had a terrible crash and massive data loss failure.")
    assert neg["status"] == "ok"
    assert neg["sentiment"] == "negative"
    assert neg["score"] < 0

    neutral = TOOL_FUNCTIONS["sentiment_analyzer"](text="The report was published yesterday afternoon.")
    assert neutral["status"] == "ok"
    assert neutral["sentiment"] == "neutral"
    assert neutral["score"] == 0.0
