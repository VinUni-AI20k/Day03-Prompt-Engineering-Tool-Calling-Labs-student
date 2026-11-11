"""Offline tests for starter tools and team-added source curation tools.

Patterns are also available in test_tools_examples.py. Fixtures are in conftest.py.

Rules:
- Offline only: mock HTTP with `fake_http`, set fake keys with `monkeypatch.setenv`.
- One behaviour per test. Name the test after the behaviour, not the function.
- Done = `pytest tests/ -v` shows 0 skipped, 0 failed.
"""
from __future__ import annotations

from copy import deepcopy

import pytest

from conftest import FakeResponse
from tools import TOOL_FUNCTIONS


# ---------------- clarify ----------------

def test_clarify_choice_returns_options_and_awaits_user() -> None:
    # Call clarify with response_type="choice" and 2 options.
    # Assert: options are returned unchanged, awaiting_user is True.
    result = TOOL_FUNCTIONS["clarify"](
        question="Which format do you prefer?",
        response_type="choice",
        options=["Brief", "Detailed"],
    )

    assert result["response_type"] == "choice"
    assert result["options"] == ["Brief", "Detailed"]
    assert result["awaiting_user"] is True


# ---------------- format ----------------

def test_format_sections_groups_items_by_section() -> None:
    # Items with section "A", "B", "A" -> markdown has exactly one "## A" and one "## B".
    result = TOOL_FUNCTIONS["format"](items=[
        {"section": "A", "title": "First"},
        {"section": "B", "title": "Second"},
        {"section": "A", "title": "Third"},
    ], template="sections")

    assert result["markdown"].count("## A") == 1
    assert result["markdown"].count("## B") == 1
    assert result["item_count"] == 3


def test_format_thread_numbers_items() -> None:
    # template="thread" -> lines start with "1/", "2/", ...
    result = TOOL_FUNCTIONS["format"](items=[
        {"title": "First"}, {"title": "Second"}, {"title": "Third"},
    ], template="thread")
    lines = [line for line in result["markdown"].splitlines() if line]

    assert [line.split(" ", 1)[0] for line in lines] == ["1/", "2/", "3/"]


@pytest.mark.parametrize("items", [None, []])
def test_format_empty_items_does_not_crash(items) -> None:
    # items=None and items=[] -> item_count == 0, no exception.
    result = TOOL_FUNCTIONS["format"](items=items, template="sections")

    assert result["item_count"] == 0
    assert result["markdown"] == ""


# ---------------- send (guardrail) ----------------

def test_send_confirmed_posts_to_telegram(monkeypatch, fake_http) -> None:
    # Set TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID, mock HTTP.
    # Assert: exactly one POST, URL contains the token, json has chat_id + text, status == "sent".
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test-bot-token")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "-100123")
    calls = fake_http(FakeResponse({"ok": True, "result": {"message_id": 1}}))

    result = TOOL_FUNCTIONS["send"](text="Research update", confirmed=True)

    assert len(calls) == 1
    assert calls[0]["method"] == "POST"
    assert calls[0]["url"] == "https://api.telegram.org/bottest-bot-token/sendMessage"
    assert calls[0]["json"]["chat_id"] == "-100123"
    assert calls[0]["json"]["text"] == "Research update"
    assert result["status"] == "sent"


def test_send_confirmed_without_env_returns_error_and_no_request(fake_http) -> None:
    calls = fake_http(FakeResponse({"ok": True}))

    result = TOOL_FUNCTIONS["send"](text="Research update", confirmed=True)

    assert result["error"] == "RuntimeError"
    assert "TELEGRAM_BOT_TOKEN" in result["message"]
    assert calls == []


# ---------------- lookup ----------------

def test_lookup_without_timeframe_omits_time_range(monkeypatch, fake_http) -> None:
    # timeframe=None -> request body has no "time_range" key.
    monkeypatch.setenv("TAVILY_API_KEY", "test-tavily-key")
    calls = fake_http(FakeResponse({"results": []}))

    result = TOOL_FUNCTIONS["lookup"](query="AI", timeframe=None)

    assert "time_range" not in calls[0]["json"]
    assert result["timeframe"] is None


# ---------------- fetch ----------------

def test_fetch_maps_firecrawl_response(monkeypatch, fake_http) -> None:
    # Mock {"data": {"markdown": "...", "metadata": {"title": "T", "sourceURL": "https://..."}}}
    # Assert title/url/source/summary in result["items"][0].
    monkeypatch.setenv("FIRECRAWL_API_KEY", "test-firecrawl-key")
    calls = fake_http(FakeResponse({"data": {
        "markdown": "Page summary",
        "metadata": {"title": "T", "sourceURL": "https://example.com/article"},
    }}))

    result = TOOL_FUNCTIONS["fetch"](url="https://example.com/article")

    assert calls[0]["url"] == "https://api.firecrawl.dev/v1/scrape"
    assert result["items"][0] == {
        "title": "T",
        "url": "https://example.com/article",
        "source": "example.com",
        "summary": "Page summary",
    }


def test_fetch_truncates_markdown_to_4000_chars(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("FIRECRAWL_API_KEY", "test-firecrawl-key")
    fake_http(FakeResponse({"data": {"markdown": "x" * 4500, "metadata": {}}}))

    result = TOOL_FUNCTIONS["fetch"](url="https://example.com/long")

    assert len(result["items"][0]["summary"]) == 4000


# ---------------- timeline / social_search ----------------

def test_timeline_respects_limit_and_skips_items_without_id(monkeypatch, fake_http) -> None:
    # Mock {"timeline": [...]} with 1 item missing tweet_id and 6 valid items, limit=3.
    # Assert 3 items, and each url looks like https://x.com/<handle>/status/<id>.
    monkeypatch.setenv("RAPIDAPI_KEY", "test-rapid-key")
    payload = {"timeline": [
        {"screen_name": "researcher", "text": "missing id"},
        *[{"screen_name": "researcher", "tweet_id": str(i), "text": f"Post {i}"} for i in range(1, 7)],
    ]}
    calls = fake_http(FakeResponse(payload))

    result = TOOL_FUNCTIONS["timeline"](screenname="researcher", limit=3)

    assert len(result["items"]) == 3
    assert all(item["url"] == f"https://x.com/researcher/status/{index}" for index, item in enumerate(result["items"], 1))
    assert calls[0]["params"] == {"screenname": "researcher"}


def test_social_search_passes_search_type(monkeypatch, fake_http) -> None:
    # Assert the request params carry the query and search_type ("Top" / "Latest").
    monkeypatch.setenv("RAPIDAPI_KEY", "test-rapid-key")
    calls = fake_http(FakeResponse({"tweets": []}))

    result = TOOL_FUNCTIONS["social_search"](query="OpenAI", search_type="Top", limit=2)

    assert calls[0]["params"]["query"] == "OpenAI"
    assert calls[0]["params"]["search_type"] == "Top"
    assert result["search_type"] == "Top"


# ---------------- policy (local knowledge + trust boundary) ----------------

def test_policy_empty_query_returns_no_results() -> None:
    result = TOOL_FUNCTIONS["policy"](query="   ")

    assert result["results"] == []
    assert result["query"] == "   "


def test_policy_area_filter_only_returns_that_area() -> None:
    # policy_area="data_privacy" -> every result has policy_area == "data_privacy".
    result = TOOL_FUNCTIONS["policy"](query="personal data", policy_area="data_privacy")

    assert result["results"]
    assert all(item["policy_area"] == "data_privacy" for item in result["results"])


def test_policy_instruction_like_lines_go_to_untrusted_text() -> None:
    # One policy file contains a quoted line that tries to give the assistant orders.
    # Query that section (source_citation) and assert: that line is in untrusted_text, NOT in facts.
    result = TOOL_FUNCTIONS["policy"](
        query="citation policy viral tweet verified fact",
        policy_area="source_citation",
        top_k=10,
    )

    injection = next(item for item in result["results"] if item["section"] == "Injection probe")
    assert "ignore the citation policy" in " ".join(injection["untrusted_text"])
    assert "ignore the citation policy" not in injection["facts"]


# ---------------- YOUR NEW TOOL(S) ----------------
# Write at least 3 tests per tool your team adds:
#   1. happy path (mocked if it calls an API)
#   2. bad / missing input from the model (empty string, wrong type, out-of-enum value)
#   3. failure path (missing key, HTTP error, timeout) -> returns error dict, does not raise

def test_dedupe_sources_keeps_first_item_and_order_after_removing_tracking_and_fragment() -> None:
    items = [
        {"url": "https://example.com/paper?id=7&utm_source=news#intro", "title": "First", "metadata": {"score": 1}},
        {"url": "https://example.com/paper?id=7&utm_medium=email&utm_campaign=launch#summary", "title": "Duplicate"},
        {"url": "https://example.com/other", "summary": "Another source"},
        {"url": "https://example.com/paper?id=7", "title": "Third copy"},
    ]
    before = deepcopy(items)
    result = TOOL_FUNCTIONS["dedupe_sources"](items=items)

    assert result == {"tool": "dedupe_sources", "items": [items[0], items[2]], "duplicate_count": 2}
    assert result["items"][0] is items[0]
    assert items == before


@pytest.mark.parametrize("items", [None, {}, {"url": "https://example.com"}, "", "not a list", 42, True, ()])
def test_dedupe_sources_wrong_items_type_returns_error_dict(items) -> None:
    result = TOOL_FUNCTIONS["dedupe_sources"](items=items)

    assert result == {
        "tool": "dedupe_sources", "error": "TypeError",
        "message": "items must be a list of research item objects",
    }


@pytest.mark.parametrize("item", [
    {}, {"title": "Missing URL"}, {"url": None}, {"url": ""}, {"url": 42}, {"url": []},
    {"url": "example.com/paper"}, {"url": "/paper"}, {"url": "https:///paper"},
    {"url": "ftp://example.com/paper"}, {"url": "javascript:alert(1)"},
    {"url": "https://exa mple.com/paper"}, {"url": "https://example.com/pa\nper"},
    {"url": "https://example.com/pa\x00per"}, {"url": "https://[invalid]/paper"},
    {"url": "https://example.com:bad/paper"}, {"url": "https://example.com:65536/paper"},
    {"url": "https://example.com/%ZZ"}, {"url": "https://example.com\\paper"},
    {"url": "https://-bad.example/paper"}, {"url": "https://bad..example/paper"},
    {"url": "https://bad^host/paper"}, {"url": "https://example.com../paper"},
])
def test_dedupe_sources_missing_or_invalid_url_returns_error_without_partial_items(item) -> None:
    result = TOOL_FUNCTIONS["dedupe_sources"](items=[{"url": "https://example.com/valid"}, item])

    assert result["tool"] == "dedupe_sources"
    assert result["error"] == "ValueError"
    assert "items[1].url" in result["message"]
    assert "items" not in result
    assert "duplicate_count" not in result


@pytest.mark.parametrize("item", [None, [], "https://example.com/paper", 42])
def test_dedupe_sources_non_object_item_returns_error_dict(item) -> None:
    result = TOOL_FUNCTIONS["dedupe_sources"](items=[item])

    assert result == {
        "tool": "dedupe_sources", "error": "TypeError",
        "message": "items[0] must be an object with a url",
    }


def test_dedupe_sources_missing_items_returns_error_dict() -> None:
    result = TOOL_FUNCTIONS["dedupe_sources"]()

    assert result["tool"] == "dedupe_sources"
    assert result["error"] == "TypeError"


def test_dedupe_sources_empty_list_returns_zero_duplicates() -> None:
    assert TOOL_FUNCTIONS["dedupe_sources"](items=[]) == {
        "tool": "dedupe_sources", "items": [], "duplicate_count": 0,
    }


@pytest.mark.parametrize("tracking_key", [
    "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content",
    "UTM_SOURCE", "%75tm_source", "fbclid", "gclid", "dclid", "msclkid", "mc_cid", "mc_eid",
])
def test_dedupe_sources_ignores_common_tracking_keys(tracking_key: str) -> None:
    items = [
        {"url": f"HTTPS://EXAMPLE.COM/paper?{tracking_key}=news&id=7#intro"},
        {"url": "https://example.com/paper?id=7"},
    ]
    result = TOOL_FUNCTIONS["dedupe_sources"](items=items)

    assert result == {"tool": "dedupe_sources", "items": [items[0]], "duplicate_count": 1}


def test_dedupe_sources_preserves_meaningful_query_fields_verbatim() -> None:
    urls = [
        "https://example.com/paper?id=1", "https://example.com/paper?id=2",
        "https://example.com/paper?page=1", "https://example.com/paper?page=2",
        "https://example.com/paper?ref=a", "https://example.com/paper?ref=b",
        "https://example.com/paper?source=a", "https://example.com/paper?source=b",
        "https://example.com/paper?q=a%26b", "https://example.com/paper?q=a&b",
        "https://example.com/paper?tag=a&tag=b", "https://example.com/paper?tag=b&tag=a",
        "https://example.com/paper?flag", "https://example.com/paper?flag=",
    ]
    items = [{"url": url} for url in urls]
    items.append({"url": urls[8] + "&utm_source=news#intro"})
    result = TOOL_FUNCTIONS["dedupe_sources"](items=items)

    assert result == {"tool": "dedupe_sources", "items": items[:-1], "duplicate_count": 1}


def test_dedupe_sources_keeps_distinct_schemes_paths_slashes_and_ports() -> None:
    items = [{"url": url} for url in [
        "http://example.com/paper", "https://example.com/paper",
        "https://example.com/Paper", "https://example.com/paper/",
        "https://example.com:443/paper", "https://example.com:8443/paper",
    ]]

    assert TOOL_FUNCTIONS["dedupe_sources"](items=items) == {
        "tool": "dedupe_sources", "items": items, "duplicate_count": 0,
    }


@pytest.mark.parametrize("url", [
    "https://[::1]/paper", "https://ví-dụ.vn/paper",
    "https://example.com/paper?q=%20", "https://example.com./paper",
])
def test_dedupe_sources_accepts_ipv6_unicode_hosts_and_valid_percent_escapes(url: str) -> None:
    items = [{"url": url}, {"url": url + "#intro"}]

    assert TOOL_FUNCTIONS["dedupe_sources"](items=items) == {
        "tool": "dedupe_sources", "items": [items[0]], "duplicate_count": 1,
    }


# ---------------- bonus source curation tools ----------------

def test_rank_sources_sorts_scores_and_applies_limit() -> None:
    items = [
        {"title": "Low", "score": 0.2},
        {"title": "High", "score": 0.9},
        {"title": "No score"},
        {"title": "Tie", "score": 0.9},
    ]

    result = TOOL_FUNCTIONS["rank_sources"](items=items, limit=2)

    assert [item["title"] for item in result["items"]] == ["High", "Tie"]
    assert result["item_count"] == 2


def test_rank_sources_rejects_non_list_items() -> None:
    result = TOOL_FUNCTIONS["rank_sources"](items={"title": "Not a list"})

    assert result["error"] == "TypeError"
    assert "items must be a list" in result["message"]


def test_rank_sources_returns_error_for_invalid_score() -> None:
    result = TOOL_FUNCTIONS["rank_sources"](items=[{"title": "Bad score", "score": "high"}])

    assert result["error"] == "ValueError"
    assert "score must be a finite number" in result["message"]


def test_filter_sources_matches_domain_and_minimum_score() -> None:
    items = [
        {"url": "https://www.Example.com/a", "score": 0.8},
        {"url": "https://example.com/b", "score": 0.4},
        {"url": "https://other.com/c", "score": 0.9},
    ]

    result = TOOL_FUNCTIONS["filter_sources"](items=items, domains=["example.com"], min_score=0.7)

    assert result["items"] == [items[0]]
    assert result["item_count"] == 1


def test_filter_sources_rejects_wrong_items_type() -> None:
    result = TOOL_FUNCTIONS["filter_sources"](items="not a list")

    assert result["error"] == "TypeError"
    assert "items must be a list" in result["message"]


def test_filter_sources_returns_error_when_score_filter_has_missing_score() -> None:
    result = TOOL_FUNCTIONS["filter_sources"](
        items=[{"url": "https://example.com/article"}], min_score=0.5,
    )

    assert result["error"] == "ValueError"
    assert "score must be a finite number" in result["message"]


def test_group_sources_groups_by_domain_in_first_seen_order() -> None:
    items = [
        {"url": "https://www.example.com/a", "title": "A"},
        {"url": "https://other.com/b", "title": "B"},
        {"url": "https://example.com/c", "title": "C"},
    ]

    result = TOOL_FUNCTIONS["group_sources"](items=items, group_by="domain")

    assert [group["key"] for group in result["groups"]] == ["example.com", "other.com"]
    assert result["groups"][0]["items"] == [items[0], items[2]]
    assert result["group_count"] == 2


def test_group_sources_rejects_unsupported_group_key() -> None:
    result = TOOL_FUNCTIONS["group_sources"](items=[], group_by="author")

    assert result["error"] == "ValueError"
    assert "group_by must be one of" in result["message"]


def test_group_sources_returns_error_for_non_object_item() -> None:
    result = TOOL_FUNCTIONS["group_sources"](items=[None], group_by="source")

    assert result["error"] == "TypeError"
    assert "items[0] must be an object" in result["message"]
