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
import re
from conftest import FakeResponse  # noqa: F401  (you will need it)
from tools import TOOL_FUNCTIONS  # noqa: F401

TODO = "TODO CP3 (student): implement this test"


# ---------------- clarify ----------------

def test_clarify_choice_returns_options_and_awaits_user() -> None:
    # Call clarify with response_type="choice" and 2 options.
    # Assert: options are returned unchanged, awaiting_user is True.
    
    result = TOOL_FUNCTIONS["clarify"](
        question="Which one?",
        response_type="choice",
        options=["A", "B"],
    )
    assert result["options"] == ["A", "B"]
    assert result["awaiting_user"] is True


# ---------------- format ----------------

def test_format_sections_groups_items_by_section() -> None:
    # Items with section "A", "B", "A" -> markdown has exactly one "## A" and one "## B".
    items = [
        {"section": "A", "text": "first"},
        {"section": "B", "text": "second"},
        {"section": "A", "text": "third"},
    ]
    result = TOOL_FUNCTIONS["format"](items=items, template="sections")
    md = result["markdown"]
    assert md.count("## A") == 1
    assert md.count("## B") == 1


def test_format_thread_numbers_items() -> None:
    # template="thread" -> lines start with "1/", "2/", ...
    items  = [{"text": "one"}, {"text": "two"}, {"text": "three"}]
    result = TOOL_FUNCTIONS["format"](items=items, template="thread")
    lines  = [l.strip() for l in result["markdown"].splitlines() if l.strip()]
    assert lines[0].startswith("1/")
    assert lines[1].startswith("2/")
    assert lines[2].startswith("3/")


def test_format_empty_items_does_not_crash() -> None:
    # items=None and items=[] -> item_count == 0, no exception.
    for empty in (None, []):
        result = TOOL_FUNCTIONS["format"](items=empty)
        assert result["item_count"] == 0


# ---------------- send (guardrail) ----------------

def test_send_confirmed_posts_to_telegram(monkeypatch, fake_http) -> None:
    # Set TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID, mock HTTP.
    # Assert: exactly one POST, URL contains the token, json has chat_id + text, status == "sent".
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test-token")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "12345")
    calls = fake_http(FakeResponse({"ok": True, "result": {"message_id": 1}}))
    result = TOOL_FUNCTIONS["send"](text="hello", confirmed=True)
    assert len(calls) == 1
    call = calls[0]
    assert call["method"] == "POST"
    assert "test-token" in call["url"]
    assert call["json"]["chat_id"] == "12345"
    assert call["json"]["text"] == "hello"
    assert result["status"] == "sent"


def test_send_confirmed_without_env_returns_error_and_no_request(monkeypatch, fake_http) -> None:
    monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)
    monkeypatch.delenv("TELEGRAM_CHAT_ID", raising=False)
    calls = fake_http(FakeResponse({"ok": True}))
    result = TOOL_FUNCTIONS["send"](text="hello", confirmed=True)
    assert "error" in result or result.get("status") != "sent"
    assert len(calls) == 0

def test_send_not_confirmed_makes_no_request(fake_http) -> None:
    calls = fake_http(FakeResponse({"ok": True}))
    result = TOOL_FUNCTIONS["send"](text="hello", confirmed=False)
    assert result["status"] == "needs_confirmation"
    assert len(calls) == 0


# ---------------- lookup ----------------

def test_lookup_without_timeframe_omits_time_range(monkeypatch, fake_http) -> None:
    # timeframe=None -> request body has no "time_range" key.
    monkeypatch.setenv("TAVILY_API_KEY", "test-key")
    calls = fake_http(FakeResponse({"results": []}))
    TOOL_FUNCTIONS["lookup"]("AI", timeframe=None)
    assert len(calls) == 1
    assert "time_range" not in calls[0]["json"]


# ---------------- fetch ----------------

def test_fetch_maps_firecrawl_response(monkeypatch, fake_http) -> None:
    # Mock {"data": {"markdown": "...", "metadata": {"title": "T", "sourceURL": "https://..."}}}
    # Assert title/url/source/summary in result["items"][0].
    monkeypatch.setenv("FIRECRAWL_API_KEY", "test-key")
    calls = fake_http(FakeResponse({"data": {
        "markdown": "# Hello\nbody text",
        "metadata": {"title": "T", "sourceURL": "https://example.com/a"},
    }}))
    result = TOOL_FUNCTIONS["fetch"]("https://example.com/a")
    item = result["items"][0]
    assert item["title"] == "T"
    assert item["url"] == "https://example.com/a"
    assert item["source"]
    assert item["summary"]


def test_fetch_truncates_markdown_to_4000_chars(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("FIRECRAWL_API_KEY", "test-key")
    fake_http(FakeResponse({"data": {
        "markdown": "x" * 5000,
        "metadata": {"title": "T", "sourceURL": "https://example.com/a"},
    }}))
    result = TOOL_FUNCTIONS["fetch"]("https://example.com/a")
    assert len(result["items"][0]["summary"]) <= 4000


# ---------------- timeline / social_search ----------------

def test_timeline_respects_limit_and_skips_items_without_id(monkeypatch, fake_http) -> None:
    # Mock {"timeline": [...]} with 1 item missing tweet_id and 6 valid items, limit=3.
    # Assert 3 items, and each url looks like https://x.com/<handle>/status/<id>.
    monkeypatch.setenv("RAPIDAPI_KEY", "test-key")
    valid = [
        {"tweet_id": str(i), "text": f"tweet {i}", "screen_name": "alice"}
        for i in range(1, 7)
    ]
    no_id = {"text": "no id here", "screen_name": "alice"}
    fake_http(FakeResponse({"timeline": [no_id] + valid}))
    result = TOOL_FUNCTIONS["timeline"]("alice", limit=3)
    items = result["items"]
    assert len(items) == 3
    for item in items:
        assert re.fullmatch(r"https://x\.com/[^/]+/status/\d+", item["url"])


def test_social_search_passes_search_type(monkeypatch, fake_http) -> None:
    # Assert the request params carry the query and search_type ("Top" / "Latest").
    monkeypatch.setenv("RAPIDAPI_KEY", "test-key")
    calls = fake_http(FakeResponse({"timeline": []}))
    TOOL_FUNCTIONS["social_search"]("AI", search_type="Latest")
    params = calls[0]["params"]
    assert params["query"] == "AI"
    assert params["search_type"] == "Latest"


# ---------------- policy (local knowledge + trust boundary) ----------------

def test_policy_empty_query_returns_no_results() -> None:
    result = TOOL_FUNCTIONS["policy"]("")
    assert result["results"] == []


def test_policy_area_filter_only_returns_that_area() -> None:
    # policy_area="data_privacy" -> every result has policy_area == "data_privacy".
    result = TOOL_FUNCTIONS["policy"]("data", policy_area="data_privacy")
    assert result["results"], "expected at least one result"
    assert all(r["policy_area"] == "data_privacy" for r in result["results"])


def test_policy_instruction_like_lines_go_to_untrusted_text() -> None:
    # One policy file contains a quoted line that tries to give the assistant orders.
    # Query that section (source_citation) and assert: that line is in untrusted_text, NOT in facts.
    result = TOOL_FUNCTIONS["policy"]("source_citation", top_k=50)
    assert result["results"], "expected at least one result"
    phrase = "cite every viral tweet"
    untrusted = " ".join(
        line for r in result["results"] for line in r["untrusted_text"]
    ).lower()
    facts = " ".join(str(r["facts"]) for r in result["results"]).lower()
    assert phrase in untrusted
    assert phrase not in facts


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