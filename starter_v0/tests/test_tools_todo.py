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

def test_my_new_tool_happy_path() -> None:
    pytest.skip(TODO)


def test_my_new_tool_bad_input_from_model() -> None:
    pytest.skip(TODO)


def test_my_new_tool_failure_returns_error_dict() -> None:
    pytest.skip(TODO)

# ---------------- github_repo (tool mới của nhóm) ----------------

def test_github_repo_maps_api_fields_and_calls_correct_url(fake_http) -> None:
    calls = fake_http(FakeResponse({"full_name": "openai/whisper", "stargazers_count": 70000,
                                    "forks_count": 8000, "language": "Python",
                                    "license": {"spdx_id": "MIT"}, "html_url": "https://github.com/openai/whisper"}))
    result = TOOL_FUNCTIONS["github_repo"](repo="https://github.com/openai/whisper")
    assert calls[0]["url"] == "https://api.github.com/repos/openai/whisper"   # request gửi đi
    assert result["stars"] == 70000 and result["license"] == "MIT"           # kết quả trả về


def test_github_repo_rejects_bad_repo_without_network(fake_http) -> None:
    calls = fake_http(FakeResponse({}))
    result = TOOL_FUNCTIONS["github_repo"](repo="whisper")
    assert result["error"] == "invalid_repo"
    assert calls == []


def test_github_repo_404_returns_not_found_error_dict(fake_http) -> None:
    fake_http(FakeResponse({"message": "Not Found"}, status_code=404))
    result = TOOL_FUNCTIONS["github_repo"](repo="openai/khong-ton-tai")
    assert result["error"] == "not_found"

# ---------------- pypi_package (tool mới) ----------------

def test_pypi_package_maps_api_fields_and_install_cmd(fake_http) -> None:
    fake_http(FakeResponse({
        "info": {"name": "openai", "version": "1.50.0", "summary": "OpenAI Python API", "license": "Apache-2.0", "requires_python": ">=3.8"},
        "urls": [{"upload_time_iso_8601": "2026-10-01T12:00:00Z"}]
    }))
    result = TOOL_FUNCTIONS["pypi_package"](package="openai")
    assert result["tool"] == "pypi_package"
    assert result["version"] == "1.50.0"
    assert result["install"] == "pip install openai==1.50.0"


def test_pypi_package_rejects_empty_or_invalid_name_without_network(fake_http) -> None:
    calls = fake_http(FakeResponse({}))
    result = TOOL_FUNCTIONS["pypi_package"](package="")
    assert result["error"] == "invalid_package"
    assert calls == []


def test_pypi_package_404_returns_not_found_error_dict(fake_http) -> None:
    fake_http(FakeResponse({"message": "Not Found"}, status_code=404))
    result = TOOL_FUNCTIONS["pypi_package"](package="khong_ton_tai_12345")
    assert result["error"] == "not_found"

# ---------------- wiki_summary (tool mới) ----------------

def test_wiki_summary_sends_user_agent_and_maps_fields(fake_http) -> None:
    calls = fake_http(FakeResponse({
        "title": "Retrieval-augmented generation",
        "description": "AI technique",
        "extract": "RAG improves LLM outputs...",
        "type": "standard",
        "content_urls": {"desktop": {"page": "https://en.wikipedia.org/wiki/Retrieval-augmented_generation"}}
    }))
    result = TOOL_FUNCTIONS["wiki_summary"](title="Retrieval-augmented generation", lang="en")
    assert "/page/summary/Retrieval-augmented_generation" in calls[0]["url"]
    assert "AI20k-Day03" in calls[0]["headers"].get("User-Agent", "")
    assert result["extract"] == "RAG improves LLM outputs..."


def test_wiki_summary_rejects_empty_title_without_network(fake_http) -> None:
    calls = fake_http(FakeResponse({}))
    result = TOOL_FUNCTIONS["wiki_summary"](title="")
    assert result["error"] == "invalid_title"
    assert calls == []


def test_wiki_summary_404_returns_not_found(fake_http) -> None:
    fake_http(FakeResponse({"detail": "Page not found"}, status_code=404))
    result = TOOL_FUNCTIONS["wiki_summary"](title="UnknownConceptXYZ123")
    assert result["error"] == "not_found"

# ---------------- hn_search (tool mới) ----------------

def test_hn_search_by_date_calls_search_by_date_endpoint(fake_http) -> None:
    calls = fake_http(FakeResponse({
        "hits": [{"objectID": "123", "title": "Claude 3.7 Released", "url": "https://anthropic.com", "points": 500, "num_comments": 150}]
    }))
    result = TOOL_FUNCTIONS["hn_search"](query="Claude", sort="date", timeframe="day", limit=10)
    assert "search_by_date" in calls[0]["url"]
    assert "numericFilters" in calls[0]["params"]
    assert calls[0]["params"]["hitsPerPage"] == 10
    assert result["results"][0]["title"] == "Claude 3.7 Released"


def test_hn_search_rejects_empty_query_without_network(fake_http) -> None:
    calls = fake_http(FakeResponse({}))
    result = TOOL_FUNCTIONS["hn_search"](query="")
    assert result["error"] == "invalid_query"
    assert calls == []


def test_hn_search_clamps_bad_limits(fake_http) -> None:
    calls = fake_http(FakeResponse({"hits": []}))
    TOOL_FUNCTIONS["hn_search"](query="AI", limit=0)
    assert calls[0]["params"]["hitsPerPage"] == 1

    TOOL_FUNCTIONS["hn_search"](query="AI", limit=999)
    assert calls[1]["params"]["hitsPerPage"] == 20