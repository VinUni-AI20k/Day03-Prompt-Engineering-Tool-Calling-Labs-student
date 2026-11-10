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
import requests

from conftest import FakeResponse
from tools import TOOL_FUNCTIONS

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


# ---------------- YOUR NEW TOOL(S): hf_models & hn_search ----------------
# Write at least 3 tests per tool your team adds:
#   1. happy path (mocked if it calls an API)
#   2. bad / missing input from the model (empty string, wrong type, out-of-enum value)
#   3. failure path (missing key, HTTP error, timeout) -> returns error dict, does not raise

def test_hf_models_sends_expected_params_and_maps_results(fake_http) -> None:
    calls = fake_http(FakeResponse([
        {"author": "missing-id"},  # entry without id/modelId should be skipped
        {
            "id": "Qwen/Qwen2.5-7B-Instruct",
            "author": "Qwen",
            "pipeline_tag": "text-generation",
            "downloads": 1200000,
            "likes": 850,
            "lastModified": "2026-05-01T00:00:00Z",
            "tags": ["transformers", "safetensors"],
        },
        {
            "id": "Qwen/Qwen2.5-3B-Instruct",
            "pipeline_tag": "text-generation",
            "downloads": 500000,
            "likes": 300,
        },
    ]))

    hf_tool = TOOL_FUNCTIONS["hf_models"]
    result = hf_tool(query="Qwen2.5", task="text-generation", sort_by="likes", limit=1)

    assert len(calls) == 1
    assert calls[0]["method"] == "GET"
    assert calls[0]["url"] == "https://huggingface.co/api/models"
    assert calls[0]["params"] == {
        "search": "Qwen2.5",
        "sort": "likes",
        "direction": -1,
        "limit": 1,
        "pipeline_tag": "text-generation",
    }
    assert len(result["items"]) == 1
    item = result["items"][0]
    assert item["model_id"] == "Qwen/Qwen2.5-7B-Instruct"
    assert item["title"] == "Qwen/Qwen2.5-7B-Instruct"
    assert item["url"] == "https://huggingface.co/Qwen/Qwen2.5-7B-Instruct"
    assert item["source"] == "huggingface.co"
    assert "Downloads: 1200000" in item["summary"]


def test_hf_models_bad_input_from_model_returns_error_dict(fake_http) -> None:
    calls = fake_http(FakeResponse([]))
    hf_tool = TOOL_FUNCTIONS["hf_models"]

    assert hf_tool(query="   ")["error"] == "ValueError"
    assert hf_tool(query=123)["error"] == "ValueError"  # type: ignore[arg-type]
    assert hf_tool(query="llama", sort_by="popularity")["error"] == "ValueError"
    assert hf_tool(query="llama", limit=0)["error"] == "ValueError"
    assert hf_tool(query="llama", limit=True)["error"] == "ValueError"
    assert hf_tool(query="llama", limit="abc")["error"] == "ValueError"  # type: ignore[arg-type]
    assert calls == []


def test_hf_models_http_timeout_or_shape_error_returns_error_dict(fake_http) -> None:
    hf_tool = TOOL_FUNCTIONS["hf_models"]

    fake_http(FakeResponse(status_code=429))
    assert hf_tool(query="llama")["error"] == "HTTPError"

    fake_http(requests.Timeout("Request timed out"))
    assert hf_tool(query="llama")["error"] == "Timeout"

    fake_http(FakeResponse({"error": "unexpected dict instead of list"}))
    assert hf_tool(query="llama")["error"] == "ValueError"


def test_hn_search_uses_date_endpoint_and_maps_hits(fake_http) -> None:
    calls = fake_http(FakeResponse({
        "hits": [
            {"title": "Missing objectID"},  # should be skipped
            {
                "objectID": "42001",
                "title": "Ask HN: Best LLM eval setup?",
                "url": None,
                "author": "alice",
                "points": 150,
                "num_comments": 42,
                "created_at": "2026-06-01T10:00:00Z",
            },
            {
                "objectID": "42002",
                "story_title": "Comment on evals",
                "url": "https://example.com/eval",
                "author": "bob",
                "comment_text": "<p>Great &amp; useful benchmark!</p>",
            },
        ]
    }))

    hn_tool = TOOL_FUNCTIONS["hn_search"]
    result = hn_tool(query="LLM eval", tag="all", sort_by="date", limit=2)

    assert len(calls) == 1
    assert calls[0]["method"] == "GET"
    assert calls[0]["url"] == "https://hn.algolia.com/api/v1/search_by_date"
    assert calls[0]["params"] == {"query": "LLM eval", "hitsPerPage": 2}
    assert "tags" not in calls[0]["params"]

    assert len(result["items"]) == 2
    first, second = result["items"]
    assert first["title"] == "Ask HN: Best LLM eval setup?"
    assert first["url"] == "https://news.ycombinator.com/item?id=42001"
    assert first["source"] == "news.ycombinator.com"
    assert "Points: 150" in first["summary"]

    assert second["url"] == "https://example.com/eval"
    assert second["hn_url"] == "https://news.ycombinator.com/item?id=42002"
    assert second["summary"] == "Great & useful benchmark!"


def test_hn_search_bad_input_from_model_returns_error_dict(fake_http) -> None:
    calls = fake_http(FakeResponse({"hits": []}))
    hn_tool = TOOL_FUNCTIONS["hn_search"]

    assert hn_tool(query="")["error"] == "ValueError"
    assert hn_tool(query=None)["error"] == "ValueError"  # type: ignore[arg-type]
    assert hn_tool(query="AI", tag="video")["error"] == "ValueError"
    assert hn_tool(query="AI", sort_by="top")["error"] == "ValueError"
    assert hn_tool(query="AI", limit=-1)["error"] == "ValueError"
    assert hn_tool(query="AI", limit="xyz")["error"] == "ValueError"  # type: ignore[arg-type]
    assert calls == []


def test_hn_search_network_or_shape_error_returns_error_dict(fake_http) -> None:
    hn_tool = TOOL_FUNCTIONS["hn_search"]

    fake_http(FakeResponse(status_code=503))
    assert hn_tool(query="AI")["error"] == "HTTPError"

    fake_http(requests.Timeout("Request timed out"))
    assert hn_tool(query="AI")["error"] == "Timeout"

    fake_http(FakeResponse({"unexpected": []}))
    assert hn_tool(query="AI")["error"] == "ValueError"


# ---------------- YOUR NEW TOOL(S): github_repos & pypi_package ----------------

def test_github_repos_sends_qualifiers_and_maps_results(monkeypatch, fake_http) -> None:
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    calls = fake_http(FakeResponse({
        "items": [
            {
                "full_name": "org/agent-one",
                "html_url": "https://github.com/org/agent-one",
                "description": "First AI agent repo",
                "stargazers_count": 500,
                "forks_count": 40,
                "language": "Python",
                "created_at": "2026-01-01T00:00:00Z",
                "pushed_at": "2026-10-01T00:00:00Z",
            },
            {
                "full_name": "org/agent-two",
                "html_url": "https://github.com/org/agent-two",
                "description": "Second AI agent repo",
                "stargazers_count": 200,
                "forks_count": 15,
                "language": "Python",
                "created_at": "2026-02-01T00:00:00Z",
                "pushed_at": "2026-10-02T00:00:00Z",
            },
            {
                "full_name": "org/agent-three",
                "html_url": "https://github.com/org/agent-three",
                "description": "Should be truncated by limit=2",
                "stargazers_count": 120,
                "forks_count": 5,
                "language": "Python",
            },
        ]
    }))

    github_tool = TOOL_FUNCTIONS["github_repos"]
    result = github_tool(
        query="ai agent",
        sort_by="hot",
        timeframe="all",
        min_stars=100,
        language="python",
        limit=2,
    )

    assert len(calls) == 1
    assert calls[0]["method"] == "GET"
    assert calls[0]["url"] == "https://api.github.com/search/repositories"
    assert "Authorization" not in calls[0]["headers"]
    params = calls[0]["params"]
    assert params["sort"] == "stars"
    assert params["order"] == "desc"
    assert params["per_page"] == 2
    assert "ai agent" in params["q"]
    assert "language:python" in params["q"]
    assert "stars:>=100" in params["q"]
    assert "created:>=" in params["q"]

    assert result["timeframe"] == "week"
    assert len(result["items"]) == 2
    first = result["items"][0]
    assert first["title"] == "org/agent-one"
    assert first["url"] == "https://github.com/org/agent-one"
    assert first["source"] == "github.com"
    assert first["stars"] == 500
    assert isinstance(first["stars_per_day"], float)


def test_github_repos_bad_or_empty_input_is_handled_safely(fake_http) -> None:
    calls = fake_http(FakeResponse({"items": []}))
    github_tool = TOOL_FUNCTIONS["github_repos"]

    # Empty qualifiers should short-circuit without calling the network
    empty_res = github_tool(query="   ", language="", min_stars=0, timeframe="all")
    assert empty_res["items"] == []
    assert calls == []

    # Invalid enum/type/range values are safely coerced without raising
    coerced_res = github_tool(
        query="mcp",
        sort_by="invalid_sort",
        timeframe="decade",
        min_stars="-10",  # type: ignore[arg-type]
        limit="abc",  # type: ignore[arg-type]
    )
    assert len(calls) == 1
    assert calls[0]["params"]["sort"] == "stars"
    assert calls[0]["params"]["per_page"] == 5
    assert "stars:>=" not in calls[0]["params"]["q"]
    assert "created:>=" not in calls[0]["params"]["q"]
    assert coerced_res["sort_by"] == "stars"
    assert coerced_res["timeframe"] == "all"


def test_github_repos_http_or_timeout_returns_error_dict(fake_http) -> None:
    github_tool = TOOL_FUNCTIONS["github_repos"]

    fake_http(FakeResponse(status_code=403))
    err_http = github_tool(query="ai agent")
    assert err_http["tool"] == "github_repos"
    assert err_http["error"] == "HTTPError"

    fake_http(requests.Timeout("GitHub API timed out"))
    err_timeout = github_tool(query="ai agent")
    assert err_timeout["tool"] == "github_repos"
    assert err_timeout["error"] == "Timeout"


def test_pypi_package_fetches_metadata_and_optional_releases(fake_http) -> None:
    calls = fake_http(FakeResponse({
        "info": {
            "name": "fastapi",
            "version": "0.115.0",
            "summary": "FastAPI framework, high performance",
            "license_expression": "MIT",
            "requires_python": ">=3.8",
            "author": "tiangolo",
            "package_url": "https://pypi.org/project/fastapi/",
            "project_urls": {"Repository": "https://github.com/fastapi/fastapi"},
        },
        "releases": {
            "0.110.0": [],
            "0.111.0": [],
            "0.112.0": [],
            "0.113.0": [],
            "0.114.0": [],
            "0.115.0": [{"upload_time_iso_8601": "2026-01-01T00:00:00Z"}],
        },
    }))

    pypi_tool = TOOL_FUNCTIONS["pypi_package"]
    result = pypi_tool(package_name=" fastapi ", include_releases="true")  # type: ignore[arg-type]

    assert len(calls) == 1
    assert calls[0]["method"] == "GET"
    assert calls[0]["url"] == "https://pypi.org/pypi/fastapi/json"
    assert result["package_name"] == "fastapi"
    assert result["version"] == "0.115.0"
    assert result["recent_versions"] == ["0.111.0", "0.112.0", "0.113.0", "0.114.0", "0.115.0"]
    item = result["items"][0]
    assert item["title"] == "fastapi (0.115.0)"
    assert item["url"] == "https://pypi.org/project/fastapi/"
    assert item["source"] == "pypi.org"
    assert item["license"] == "MIT"
    assert item["requires_python"] == ">=3.8"
    assert item["latest_release_date"] == "2026-01-01T00:00:00Z"


def test_pypi_package_bad_input_returns_error_dict_without_network(fake_http) -> None:
    calls = fake_http(FakeResponse({}))
    pypi_tool = TOOL_FUNCTIONS["pypi_package"]

    assert pypi_tool(package_name="")["error"] == "ValueError"
    assert pypi_tool(package_name="   ")["error"] == "ValueError"
    assert pypi_tool(package_name=None)["error"] == "ValueError"  # type: ignore[arg-type]
    assert pypi_tool(package_name="../etc/passwd")["error"] == "ValueError"
    assert pypi_tool(package_name="bad pkg!")["error"] == "ValueError"
    assert calls == []


def test_pypi_package_http_or_timeout_returns_error_dict(fake_http) -> None:
    pypi_tool = TOOL_FUNCTIONS["pypi_package"]

    fake_http(FakeResponse(status_code=404))
    err_http = pypi_tool(package_name="nonexistent-pkg")
    assert err_http["tool"] == "pypi_package"
    assert err_http["error"] == "HTTPError"

    fake_http(requests.Timeout("PyPI API timed out"))
    err_timeout = pypi_tool(package_name="fastapi")
    assert err_timeout["tool"] == "pypi_package"
    assert err_timeout["error"] == "Timeout"
