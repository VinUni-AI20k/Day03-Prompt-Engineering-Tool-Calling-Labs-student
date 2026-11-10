"""TODO CP3 (student): Tool Unit Test Challenge.

Each test below is a stub. Replace `pytest.skip(...)` with a real test.
Patterns to copy are in test_tools_examples.py. Fixtures are in conftest.py.

Rules:
- Offline only: mock HTTP with `fake_http`, set fake keys with `monkeypatch.setenv`.
- One behaviour per test. Name the test after the behaviour, not the function.
- Done = `pytest tests/ -v` shows 0 skipped, 0 failed.
"""

from __future__ import annotations

from conftest import FakeResponse
from tools import TOOL_FUNCTIONS


# ---------------- clarify ----------------

def test_clarify_choice_returns_options_and_awaits_user() -> None:
    # Call clarify with response_type="choice" and 2 options.
    # Assert: options are returned unchanged, awaiting_user is True.
    opts = ["Option A", "Option B"]
    result = TOOL_FUNCTIONS["clarify"](
        question="Which option do you prefer?",
        response_type="choice",
        options=opts,
    )
    assert result["options"] == opts
    assert result["response_type"] == "choice"
    assert result["awaiting_user"] is True


# ---------------- format ----------------

def test_format_sections_groups_items_by_section() -> None:
    # Items with section "A", "B", "A" -> markdown has exactly one "## A" and one "## B".
    items = [
        {"title": "Item 1", "section": "A", "url": "https://a.com/1"},
        {"title": "Item 2", "section": "B", "url": "https://b.com/2"},
        {"title": "Item 3", "section": "A", "url": "https://a.com/3"},
    ]
    result = TOOL_FUNCTIONS["format"](items=items, template="sections", headline="Digest")
    md = result["markdown"]
    assert md.count("## A") == 1
    assert md.count("## B") == 1
    assert result["item_count"] == 3


def test_format_thread_numbers_items() -> None:
    # template="thread" -> lines start with "1/", "2/", ...
    items = [
        {"title": "First post", "url": "https://example.com/1"},
        {"title": "Second post", "url": "https://example.com/2"},
    ]
    result = TOOL_FUNCTIONS["format"](items=items, template="thread")
    chunks = result["markdown"].split("\n\n")
    assert chunks[0].startswith("1/ ")
    assert chunks[1].startswith("2/ ")


def test_format_empty_items_does_not_crash() -> None:
    # items=None and items=[] -> item_count == 0, no exception.
    res_none = TOOL_FUNCTIONS["format"](items=None)
    res_empty = TOOL_FUNCTIONS["format"](items=[])
    assert res_none["item_count"] == 0
    assert res_empty["item_count"] == 0


# ---------------- send (guardrail) ----------------

def test_send_confirmed_posts_to_telegram(monkeypatch, fake_http) -> None:
    # Set TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID, mock HTTP.
    # Assert: exactly one POST, URL contains the token, json has chat_id + text, status == "sent".
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "bot123456:ABCDEF")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "-100987654321")
    calls = fake_http(FakeResponse({"ok": True}))

    result = TOOL_FUNCTIONS["send"](text="Hello team!", confirmed=True)

    assert len(calls) == 1
    assert calls[0]["method"] == "POST"
    assert "bot123456:ABCDEF" in calls[0]["url"]
    assert calls[0]["json"]["chat_id"] == "-100987654321"
    assert calls[0]["json"]["text"] == "Hello team!"
    assert result["status"] == "sent"


def test_send_confirmed_without_env_returns_error_and_no_request(fake_http) -> None:
    calls = fake_http(FakeResponse({"ok": True}))
    result = TOOL_FUNCTIONS["send"](text="Hello team!", confirmed=True)

    assert calls == []
    assert result["error"] == "RuntimeError"
    assert "TELEGRAM_BOT_TOKEN" in result["message"]


# ---------------- lookup ----------------

def test_lookup_without_timeframe_omits_time_range(monkeypatch, fake_http) -> None:
    # timeframe=None -> request body has no "time_range" key.
    monkeypatch.setenv("TAVILY_API_KEY", "test-tavily-key")
    calls = fake_http(FakeResponse({"results": []}))

    TOOL_FUNCTIONS["lookup"](query="AI agents", topic="general", timeframe=None, max_results=3)

    assert len(calls) == 1
    assert "time_range" not in calls[0]["json"]


# ---------------- fetch ----------------

def test_fetch_maps_firecrawl_response(monkeypatch, fake_http) -> None:
    # Mock {"data": {"markdown": "...", "metadata": {"title": "T", "sourceURL": "https://..."}}}
    # Assert title/url/source/summary in result["items"][0].
    monkeypatch.setenv("FIRECRAWL_API_KEY", "fc-test-key")
    calls = fake_http(FakeResponse({
        "data": {
            "markdown": "Hello Firecrawl content",
            "metadata": {
                "title": "My Page Title",
                "sourceURL": "https://www.example.com/article",
            },
        }
    }))

    result = TOOL_FUNCTIONS["fetch"](url="https://www.example.com/article")

    assert len(calls) == 1
    item = result["items"][0]
    assert item["title"] == "My Page Title"
    assert item["url"] == "https://www.example.com/article"
    assert item["source"] == "example.com"
    assert item["summary"] == "Hello Firecrawl content"


def test_fetch_truncates_markdown_to_4000_chars(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("FIRECRAWL_API_KEY", "fc-test-key")
    fake_http(FakeResponse({
        "data": {
            "markdown": "a" * 5000,
            "metadata": {"title": "Long Page", "sourceURL": "https://example.com/long"},
        }
    }))

    result = TOOL_FUNCTIONS["fetch"](url="https://example.com/long")
    summary = result["items"][0]["summary"]
    assert len(summary) == 4000
    assert summary == "a" * 4000


# ---------------- timeline / social_search ----------------

def test_timeline_respects_limit_and_skips_items_without_id(monkeypatch, fake_http) -> None:
    # Mock {"timeline": [...]} with 1 item missing tweet_id and 6 valid items, limit=3.
    # Assert 3 items, and each url looks like https://x.com/<handle>/status/<id>.
    monkeypatch.setenv("RAPIDAPI_KEY", "rapid-test-key")
    raw_timeline = [{"screen_name": "sama", "text": "Missing ID tweet"}]
    for i in range(1, 7):
        raw_timeline.append({
            "tweet_id": str(100 + i),
            "screen_name": "sama",
            "text": f"Valid tweet {i}",
        })
    fake_http(FakeResponse({"timeline": raw_timeline}))

    result = TOOL_FUNCTIONS["timeline"](screenname="sama", limit=3)

    items = result["items"]
    assert len(items) == 3
    assert items[0]["url"] == "https://x.com/sama/status/101"
    assert items[1]["url"] == "https://x.com/sama/status/102"
    assert items[2]["url"] == "https://x.com/sama/status/103"


def test_social_search_passes_search_type(monkeypatch, fake_http) -> None:
    # Assert the request params carry the query and search_type ("Top" / "Latest").
    monkeypatch.setenv("RAPIDAPI_KEY", "rapid-test-key")
    calls = fake_http(FakeResponse({"timeline": []}))

    result = TOOL_FUNCTIONS["social_search"](query="OpenAI", search_type="Top", limit=2)

    assert len(calls) == 1
    assert calls[0]["params"]["query"] == "OpenAI"
    assert calls[0]["params"]["search_type"] == "Top"
    assert result["search_type"] == "Top"


# ---------------- policy (local knowledge + trust boundary) ----------------

def test_policy_empty_query_returns_no_results() -> None:
    result = TOOL_FUNCTIONS["policy"](query="   ")
    assert result["results"] == []


def test_policy_area_filter_only_returns_that_area() -> None:
    # policy_area="data_privacy" -> every result has policy_area == "data_privacy".
    result = TOOL_FUNCTIONS["policy"](query="data policy", policy_area="data_privacy", top_k=5)
    assert len(result["results"]) > 0
    for hit in result["results"]:
        assert hit["policy_area"] == "data_privacy"


def test_policy_instruction_like_lines_go_to_untrusted_text() -> None:
    # One policy file contains a quoted line that tries to give the assistant orders.
    # Query that section (source_citation) and assert: that line is in untrusted_text, NOT in facts.
    result = TOOL_FUNCTIONS["policy"](query="source citation", policy_area="all", top_k=10)
    untrusted_hits = [r for r in result["results"] if r.get("untrusted_text")]
    assert len(untrusted_hits) > 0
    target = untrusted_hits[0]
    for line in target["untrusted_text"]:
        assert line not in target["facts"]


# ---------------- YOUR NEW TOOL(S) ----------------
# Write at least 3 tests per tool your team adds:
#   1. happy path (mocked if it calls an API)
#   2. bad / missing input from the model (empty string, wrong type, out-of-enum value)
#   3. failure path (missing key, HTTP error, timeout) -> returns error dict, does not raise

def test_text_stats_happy_path_returns_counts() -> None:
    res = TOOL_FUNCTIONS["text_stats"](text="AI agent evaluation is very important", wpm=120)
    assert res["status"] == "ok"
    assert res["tool"] == "text_stats"
    assert res["word_count"] == 6
    assert res["char_count"] == 37
    assert res["estimated_reading_seconds"] == 3.0
    assert len(res["items"]) == 1


def test_text_stats_bad_input_empty_string_from_model() -> None:
    res = TOOL_FUNCTIONS["text_stats"](text="   ")
    assert res["status"] == "error"
    assert "error" in res
    assert res["items"] == []


def test_text_stats_failure_invalid_wpm_returns_error_dict() -> None:
    res_zero = TOOL_FUNCTIONS["text_stats"](text="Hello world", wpm=0)
    assert res_zero["status"] == "error"
    assert "error" in res_zero

    res_bad_type = TOOL_FUNCTIONS["text_stats"](text="Hello world", wpm="invalid_int")
    assert res_bad_type["status"] == "error"
    assert "error" in res_bad_type


