"""TODO(student): Tool Unit Test Challenge.

The deduplicate tests are implemented; tests for the original starter tools
remain stubs. Replace their `pytest.skip(...)` calls with real tests as assigned.
Patterns to copy are in test_tools_examples.py. Fixtures are in conftest.py.

Rules:
- Offline only: mock HTTP with `fake_http`, set fake keys with `monkeypatch.setenv`.
- One behaviour per test. Name the test after the behaviour, not the function.
- The full starter challenge is done when `pytest tests/ -v` shows 0 skipped,
  0 failed; the deduplicate task leaves unrelated starter stubs unchanged.
"""
from __future__ import annotations

from copy import deepcopy

import pytest

from agent import ResearchAgent
from conftest import FakeResponse  # noqa: F401  (you will need it)
from providers.base import ModelResponse, ToolCall
from tools import TOOL_FUNCTIONS  # noqa: F401
from tools.deduplicate.tool import deduplicate

TODO = "TODO(student): implement this test"


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

def test_deduplicate_keeps_first_url_and_preserves_order_and_fields() -> None:
    items = [
        {"url": " HTTPS://Example.com/a/// ", "title": "First", "score": 0.8},
        {"url": "https://example.com/b", "summary": "Second result"},
        {"url": "https://example.com/A", "title": "Duplicate"},
        {"url": "https://example.com/c", "source": "Other"},
    ]

    result = deduplicate(items)

    assert result == {
        "tool": "deduplicate",
        "items": [items[0], items[1], items[3]],
        "removed_count": 1,
    }


def test_deduplicate_title_trims_whitespace_and_casefolds_unicode() -> None:
    items = [
        {"title": "  Straße  ", "url": "https://example.com/first"},
        {"title": "STRASSE", "url": "https://example.com/second"},
        {"title": "Different", "url": "https://example.com/first"},
    ]

    result = deduplicate(items, key_by="title")

    assert result["items"] == [items[0], items[2]]
    assert result["removed_count"] == 1


@pytest.mark.parametrize("key_by", ["url", "title"])
def test_deduplicate_retains_every_missing_none_or_empty_key(key_by) -> None:
    items = [
        {"source": "missing one"},
        {"source": "missing two"},
        {key_by: None},
        {key_by: ""},
        {key_by: " \t "},
        {key_by: ""},
    ]

    assert deduplicate(items, key_by=key_by) == {
        "tool": "deduplicate",
        "items": items,
        "removed_count": 0,
    }


def test_deduplicate_retains_urls_empty_after_removing_trailing_slashes() -> None:
    items = [{"url": "/"}, {"url": " /// "}]

    assert deduplicate(items)["items"] == items
    assert deduplicate(items)["removed_count"] == 0


def test_deduplicate_does_not_modify_input_items_or_nested_fields() -> None:
    items = [
        {"url": " HTTPS://Example.com/a/ ", "metadata": {"tags": ["keep"]}},
        {"url": "https://example.com/a", "title": "Duplicate"},
    ]
    original = deepcopy(items)

    deduplicate(items)

    assert items == original


def test_deduplicate_accepts_empty_items() -> None:
    assert deduplicate([]) == {
        "tool": "deduplicate",
        "items": [],
        "removed_count": 0,
    }


@pytest.mark.parametrize("items", [None, {}, "results", ({"url": "a"},)])
def test_deduplicate_non_list_items_returns_type_error(items) -> None:
    result = deduplicate(items)

    assert result["tool"] == "deduplicate"
    assert result["error"] == "TypeError"
    assert isinstance(result["message"], str) and result["message"]


@pytest.mark.parametrize("key_by", ["summary", "URL", "", None, []])
def test_deduplicate_unsupported_key_returns_value_error(key_by) -> None:
    result = deduplicate([], key_by=key_by)

    assert result["tool"] == "deduplicate"
    assert result["error"] == "ValueError"
    assert isinstance(result["message"], str) and result["message"]


@pytest.mark.parametrize("bad_item", [None, "result", 42, []])
def test_deduplicate_malformed_item_returns_type_error(bad_item) -> None:
    result = deduplicate([{"url": "https://example.com/valid"}, bad_item])

    assert result["tool"] == "deduplicate"
    assert result["error"] == "TypeError"
    assert isinstance(result["message"], str) and result["message"]


@pytest.mark.parametrize("key_by", ["url", "title"])
@pytest.mark.parametrize("bad_key", [42, False, [], {}])
def test_deduplicate_non_string_key_returns_type_error(key_by, bad_key) -> None:
    result = deduplicate([{key_by: bad_key}], key_by=key_by)

    assert result["tool"] == "deduplicate"
    assert result["error"] == "TypeError"
    assert isinstance(result["message"], str) and result["message"]


def test_deduplicate_only_checks_the_selected_key() -> None:
    items = [
        {"url": "https://example.com/a", "title": ["non-string metadata"]},
        {"url": "https://example.com/a", "title": None},
    ]

    result = deduplicate(items)

    assert result["items"] == [items[0]]
    assert result["removed_count"] == 1


def test_deduplicate_executes_through_agent_tool_registry() -> None:
    items = [
        {"title": " First report ", "url": "https://example.com/first"},
        {"title": "FIRST REPORT", "url": "https://example.com/duplicate"},
        {"title": "Other report", "url": "https://example.com/first"},
    ]
    arguments = {"items": items, "key_by": "title"}

    class FakeProvider:
        def complete(self, messages, tools=None, *, model=None,
                     temperature=0.0, tool_choice=None) -> ModelResponse:
            return ModelResponse(tool_calls=[ToolCall("deduplicate", arguments)])

    agent = ResearchAgent(FakeProvider(), system_prompt="Execute research tools.")

    run = agent.run([{"role": "user", "content": "Remove duplicate report titles."}])

    assert run.tool_results == [{
        "tool": "deduplicate",
        "args": arguments,
        "result": {
            "tool": "deduplicate",
            "items": [items[0], items[2]],
            "removed_count": 1,
        },
    }]
