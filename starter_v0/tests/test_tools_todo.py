"""CP3: Tool Unit Test Challenge.

Unit tests for every built-in tool stub plus the team's new tools (dedupe_sources, hn_search).
Patterns copied from test_tools_examples.py. Fixtures are in conftest.py.

Rules:
- Offline only: mock HTTP with `fake_http`, set fake keys with `monkeypatch.setenv`.
- One behaviour per test. Name the test after the behaviour, not the function.
- Done = `pytest tests/ -v` shows 0 skipped, 0 failed.
"""
from __future__ import annotations

import requests

from conftest import FakeResponse
from tools import TOOL_FUNCTIONS

clarify = TOOL_FUNCTIONS["clarify"]
format_tool = TOOL_FUNCTIONS["format"]
send = TOOL_FUNCTIONS["send"]
lookup = TOOL_FUNCTIONS["lookup"]
fetch = TOOL_FUNCTIONS["fetch"]
timeline = TOOL_FUNCTIONS["timeline"]
social_search = TOOL_FUNCTIONS["social_search"]
policy = TOOL_FUNCTIONS["policy"]
hn_search = TOOL_FUNCTIONS["hn_search"]
dedupe_sources = TOOL_FUNCTIONS["dedupe_sources"]


# ---------------- clarify ----------------

def test_clarify_choice_returns_options_and_awaits_user() -> None:
    result = clarify(question="Chọn nguồn?", response_type="choice", options=["web", "twitter"])

    assert result["options"] == ["web", "twitter"]
    assert result["response_type"] == "choice"
    assert result["awaiting_user"] is True


# ---------------- format ----------------

def test_format_sections_groups_items_by_section() -> None:
    items = [
        {"title": "a1", "section": "A"},
        {"title": "b1", "section": "B"},
        {"title": "a2", "section": "A"},
    ]
    markdown = format_tool(items=items, template="sections")["markdown"]

    assert markdown.count("## A") == 1
    assert markdown.count("## B") == 1
    assert markdown.index("a2") < markdown.index("## B")  # a2 grouped under A


def test_format_thread_numbers_items() -> None:
    items = [{"title": f"Tin {i}"} for i in range(3)]
    lines = format_tool(items=items, template="thread")["markdown"].split("\n\n")

    assert [line.split(" ")[0] for line in lines] == ["1/", "2/", "3/"]


def test_format_empty_items_does_not_crash() -> None:
    assert format_tool(items=None, template="sections")["item_count"] == 0
    assert format_tool(items=[], template="brief")["item_count"] == 0


# ---------------- send (guardrail) ----------------

def test_send_confirmed_posts_to_telegram(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "123:abc")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "-100999")
    calls = fake_http(FakeResponse({"ok": True}))

    result = send(text="Bản tin AI", confirmed=True)

    assert len(calls) == 1
    assert calls[0]["method"] == "POST"
    assert "bot123:abc/sendMessage" in calls[0]["url"]
    assert calls[0]["json"]["chat_id"] == "-100999"
    assert calls[0]["json"]["text"] == "Bản tin AI"
    assert result["status"] == "sent"


def test_send_confirmed_without_env_returns_error_and_no_request(fake_http) -> None:
    calls = fake_http(FakeResponse({"ok": True}))

    result = send(text="Bản tin", confirmed=True)

    assert result["error"] == "RuntimeError"
    assert "TELEGRAM_BOT_TOKEN" in result["message"]
    assert calls == []


# ---------------- lookup ----------------

def test_lookup_without_timeframe_omits_time_range(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("TAVILY_API_KEY", "test-key")
    calls = fake_http(FakeResponse({"results": []}))

    result = lookup(query="AI", topic="general", timeframe=None)

    assert "time_range" not in calls[0]["json"]
    assert calls[0]["json"]["query"] == "AI"
    assert result["items"] == []


# ---------------- fetch ----------------

def test_fetch_maps_firecrawl_response(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("FIRECRAWL_API_KEY", "fc-test")
    calls = fake_http(FakeResponse({"data": {
        "markdown": "# Hello\nNội dung bài",
        "metadata": {"title": "T", "sourceURL": "https://www.example.com/post"},
    }}))

    result = fetch(url="https://www.example.com/post")

    assert calls[0]["url"] == "https://api.firecrawl.dev/v1/scrape"
    assert calls[0]["json"]["url"] == "https://www.example.com/post"
    assert calls[0]["headers"]["Authorization"] == "Bearer fc-test"
    assert result["items"][0] == {
        "title": "T",
        "url": "https://www.example.com/post",
        "source": "example.com",
        "summary": "# Hello\nNội dung bài",
    }


def test_fetch_truncates_markdown_to_4000_chars(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("FIRECRAWL_API_KEY", "fc-test")
    fake_http(FakeResponse({"data": {"markdown": "x" * 5000, "metadata": {}}}))

    summary = fetch(url="https://example.com")["items"][0]["summary"]

    assert len(summary) == 4000


# ---------------- timeline / social_search ----------------

def test_timeline_respects_limit_and_skips_items_without_id(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("RAPIDAPI_KEY", "rk")
    raw = [{"text": "no id", "screen_name": "sama"}] + [
        {"tweet_id": str(i), "text": f"tweet {i}", "screen_name": "sama"} for i in range(6)
    ]
    calls = fake_http(FakeResponse({"timeline": raw}))

    result = timeline(screenname="sama", limit=3)

    assert calls[0]["params"] == {"screenname": "sama"}
    assert len(result["items"]) == 3
    assert [item["url"] for item in result["items"]] == [
        "https://x.com/sama/status/0", "https://x.com/sama/status/1", "https://x.com/sama/status/2",
    ]


def test_social_search_passes_search_type(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("RAPIDAPI_KEY", "rk")
    calls = fake_http(FakeResponse({"timeline": []}))

    social_search(query="OpenAI", search_type="Top")

    assert calls[0]["url"].endswith("/search.php")
    assert calls[0]["params"] == {"query": "OpenAI", "search_type": "Top"}
    assert calls[0]["headers"]["x-rapidapi-key"] == "rk"


# ---------------- policy (local knowledge + trust boundary) ----------------

def test_policy_empty_query_returns_no_results() -> None:
    assert policy(query="")["results"] == []


def test_policy_area_filter_only_returns_that_area() -> None:
    results = policy(query="data personal privacy", policy_area="data_privacy", top_k=5)["results"]

    assert results
    assert all(item["policy_area"] == "data_privacy" for item in results)


def test_policy_instruction_like_lines_go_to_untrusted_text() -> None:
    results = policy(query="injection probe citation", policy_area="source_citation", top_k=10)["results"]
    probe = next(item for item in results if item["section"] == "Injection probe")

    assert any("citation policy" in line for line in probe["untrusted_text"])
    assert "citation policy" not in probe["facts"]


# ---------------- NEW TOOL 1: dedupe_sources (Hà Lê Duy) ----------------

def test_dedupe_sources_preserves_order_and_counts_duplicates() -> None:
    first = "https://example.org/research"
    second = "https://example.org/research?page=2"

    result = TOOL_FUNCTIONS["dedupe_sources"](urls=[first, second, first])

    assert result == {"urls": [first, second], "duplicate_count": 1}


def test_dedupe_sources_rejects_a_string_instead_of_a_list() -> None:
    result = TOOL_FUNCTIONS["dedupe_sources"](urls="https://example.org/research")

    assert result["error"] == "invalid_input"


def test_dedupe_sources_returns_error_for_malformed_url() -> None:
    result = TOOL_FUNCTIONS["dedupe_sources"](urls=["https://[invalid"])

    assert result == {"error": "invalid_url", "message": "urls[0] must be an HTTP(S) URL with a host."}


# ---------------- NEW TOOL 2: hn_search (Nguyễn Thiên Bảo) ----------------

def test_hn_search_happy_path_sends_query_and_maps_items(fake_http) -> None:
    calls = fake_http(FakeResponse({"hits": [
        {"objectID": "42", "title": "LLM agents in prod", "url": "https://blog.dev/agents",
         "points": 120, "num_comments": 33, "created_at": "2026-11-01T00:00:00Z"},
        {"objectID": "43", "title": "Ask HN: agents?", "url": None, "points": 5},
    ]}))

    result = hn_search(query="LLM agents", limit=2)

    assert calls[0]["url"] == "https://hn.algolia.com/api/v1/search"
    assert calls[0]["params"] == {"query": "LLM agents", "tags": "story", "hitsPerPage": 2}
    assert result["items"][0] == {
        "title": "LLM agents in prod",
        "url": "https://blog.dev/agents",
        "discussion_url": "https://news.ycombinator.com/item?id=42",
        "source": "news.ycombinator.com",
        "points": 120,
        "num_comments": 33,
        "published_at": "2026-11-01T00:00:00Z",
    }
    # Story without external url falls back to the HN discussion link.
    assert result["items"][1]["url"] == "https://news.ycombinator.com/item?id=43"


def test_hn_search_sort_date_uses_search_by_date_endpoint(fake_http) -> None:
    calls = fake_http(FakeResponse({"hits": []}))

    result = hn_search(query="Rust", sort="date")

    assert calls[0]["url"] == "https://hn.algolia.com/api/v1/search_by_date"
    assert result["sort"] == "date"


def test_hn_search_empty_query_returns_error_without_request(fake_http) -> None:
    calls = fake_http(FakeResponse({"hits": []}))

    for bad in ["", "   ", None, 123]:
        result = hn_search(query=bad)
        assert result["error"] == "invalid_query"
    assert calls == []


def test_hn_search_bad_limit_and_sort_from_model_are_normalised(fake_http) -> None:
    calls = fake_http(FakeResponse({"hits": []}))

    hn_search(query="AI", limit="abc", sort="popular")   # wrong type + out-of-enum
    hn_search(query="AI", limit=0)                        # below range
    hn_search(query="AI", limit=999)                      # above range

    assert calls[0]["params"]["hitsPerPage"] == 5
    assert calls[0]["url"].endswith("/search")           # unknown sort -> relevance
    assert calls[1]["params"]["hitsPerPage"] == 1
    assert calls[2]["params"]["hitsPerPage"] == 20


def test_hn_search_http_error_returns_error_dict(fake_http) -> None:
    fake_http(FakeResponse(status_code=503))

    result = hn_search(query="AI")

    assert result["tool"] == "hn_search"
    assert result["error"] == "HTTPError"


def test_hn_search_timeout_returns_error_dict(fake_http) -> None:
    fake_http(requests.Timeout("timed out"))

    result = hn_search(query="AI")

    assert result["error"] == "Timeout"
