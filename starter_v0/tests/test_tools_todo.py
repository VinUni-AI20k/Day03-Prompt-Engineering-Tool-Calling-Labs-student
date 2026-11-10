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

import requests  # noqa: E402

hn_tool = TOOL_FUNCTIONS["hackernews_search"]
gh_tool = TOOL_FUNCTIONS["github_search"]

HN_HITS = {"hits": [
    {"objectID": "101", "title": "Show HN: tiny LLM", "url": "https://www.example.com/llm",
     "points": 321, "author": "alice", "num_comments": 45, "created_at": "2026-11-01T10:00:00Z"},
    {"objectID": "102", "title": "Ask HN: best RAG stack?", "url": None,
     "points": 12, "author": "bob", "num_comments": 7, "created_at": "2026-11-02T10:00:00Z"},
]}

GH_REPOS = {"total_count": 2, "items": [
    {"full_name": "acme/agent-kit", "html_url": "https://github.com/acme/agent-kit", "description": "Agentic AI toolkit",
     "stargazers_count": 5000, "forks_count": 300, "language": "Python", "topics": ["agents"],
     "created_at": "2026-01-05T00:00:00Z", "updated_at": "2026-11-09T00:00:00Z"},
    {"full_name": "acme/other", "html_url": "https://github.com/acme/other", "description": None,
     "stargazers_count": 10, "forks_count": 1, "language": None},
]}


# ---------------- hackernews_search ----------------

def test_hackernews_happy_path_sends_query_and_maps_hits(fake_http) -> None:
    calls = fake_http(FakeResponse(HN_HITS))
    result = hn_tool(query="LLM", tags="story", limit=2)

    assert calls[0]["method"] == "GET"
    assert calls[0]["url"] == "https://hn.algolia.com/api/v1/search"
    assert calls[0]["params"] == {"query": "LLM", "tags": "story", "hitsPerPage": 2}
    first, second = result["items"]
    assert first["title"] == "Show HN: tiny LLM"
    assert first["url"] == "https://www.example.com/llm"
    assert first["source"] == "example.com"
    assert (first["points"], first["author"], first["num_comments"]) == (321, "alice", 45)
    assert first["hn_url"] == "https://news.ycombinator.com/item?id=101"
    # Ask HN without external link falls back to the HN discussion URL.
    assert second["url"] == "https://news.ycombinator.com/item?id=102"
    assert second["source"] == "news.ycombinator.com"


def test_hackernews_sort_date_and_date_range_use_by_date_endpoint(fake_http) -> None:
    calls = fake_http(FakeResponse({"hits": []}))
    hn_tool(query="Rust", sort="date", date_from="2026-11-01", date_to="2026-11-02")

    assert calls[0]["url"] == "https://hn.algolia.com/api/v1/search_by_date"
    # 2026-11-01T00:00:00Z = 1793491200 ; 2026-11-02T23:59:59Z = 1793663999
    assert calls[0]["params"]["numericFilters"] == "created_at_i>=1793491200,created_at_i<=1793663999"


def test_hackernews_bad_input_from_model_is_normalized_or_rejected(fake_http) -> None:
    calls = fake_http(FakeResponse({"hits": []}))

    hn_tool(query="AI", tags="not_a_tag", sort="weird", limit=999)
    assert calls[0]["params"]["tags"] == "story"
    assert calls[0]["params"]["hitsPerPage"] == 20
    assert calls[0]["url"].endswith("/search")

    empty = hn_tool(query="   ")
    assert empty["error"] == "ValueError"
    bad_date = hn_tool(query="AI", date_from="01/11/2026")
    assert bad_date["error"] == "ValueError"
    assert len(calls) == 1  # no request sent for invalid input


def test_hackernews_front_page_allows_empty_query(fake_http) -> None:
    calls = fake_http(FakeResponse(HN_HITS))
    result = hn_tool(query="", tags="front_page")
    assert calls[0]["params"]["tags"] == "front_page"
    assert len(result["items"]) == 2


def test_hackernews_http_error_returns_error_dict(fake_http) -> None:
    fake_http(FakeResponse(status_code=503))
    result = hn_tool(query="LLM")
    assert result["tool"] == "hackernews_search"
    assert result["error"] == "HTTPError"


# ---------------- github_search ----------------

def test_github_happy_path_builds_qualifiers_and_maps_repos(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("GITHUB_TOKEN", "gh-test")
    calls = fake_http(FakeResponse(GH_REPOS))
    result = gh_tool(query="agentic AI", language="python", created_after="2026-01-01", limit=2)

    assert calls[0]["url"] == "https://api.github.com/search/repositories"
    assert calls[0]["params"] == {
        "q": "agentic AI language:python created:>=2026-01-01", "per_page": 2, "sort": "stars", "order": "desc",
    }
    assert calls[0]["headers"]["Authorization"] == "Bearer gh-test"
    assert result["total_count"] == 2
    repo = result["items"][0]
    assert (repo["title"], repo["url"], repo["stars"], repo["forks"], repo["language"]) == (
        "acme/agent-kit", "https://github.com/acme/agent-kit", 5000, 300, "Python",
    )
    assert repo["updated_at"] == "2026-11-09T00:00:00Z"
    # Missing description/language must not crash or leak None.
    assert result["items"][1]["description"] == ""
    assert result["items"][1]["language"] == ""


def test_github_without_token_still_works_and_sends_no_auth_header(fake_http) -> None:
    calls = fake_http(FakeResponse(GH_REPOS))
    result = gh_tool(query="RAG")
    assert "Authorization" not in calls[0]["headers"]
    assert len(result["items"]) == 2


def test_github_bad_input_from_model_is_normalized_or_rejected(fake_http) -> None:
    calls = fake_http(FakeResponse(GH_REPOS))

    gh_tool(query="RAG", sort="popularity", order="up", limit="abc")
    assert calls[0]["params"]["sort"] == "stars"
    assert calls[0]["params"]["order"] == "desc"
    assert calls[0]["params"]["per_page"] == 5

    gh_tool(query="RAG", sort="best_match")
    assert "sort" not in calls[1]["params"]

    assert gh_tool(query="")["error"] == "ValueError"
    assert gh_tool(query="RAG", created_after="last week")["error"] == "ValueError"
    assert len(calls) == 2


def test_github_rate_limit_returns_error_dict(fake_http) -> None:
    fake_http(FakeResponse({"message": "API rate limit exceeded"}, status_code=403))
    result = gh_tool(query="RAG")
    assert result["tool"] == "github_search"
    assert result["error"] == "RuntimeError"
    assert "GITHUB_TOKEN" in result["message"]


def test_github_timeout_returns_error_dict(fake_http) -> None:
    fake_http(requests.Timeout("timed out"))
    result = gh_tool(query="RAG")
    assert result["error"] == "Timeout"
