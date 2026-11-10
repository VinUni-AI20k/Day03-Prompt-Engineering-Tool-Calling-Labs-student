"""CP3: Tool Unit Test Challenge (all stubs implemented, 0 skipped).

Patterns come from test_tools_examples.py. Fixtures are in conftest.py.

Rules:
- Offline only: mock HTTP with `fake_http`, set fake keys with `monkeypatch.setenv`.
- One behaviour per test. Name the test after the behaviour, not the function.
- Done = `pytest tests/ -v` shows 0 skipped, 0 failed.
"""
from __future__ import annotations

from typing import Any

import requests

from conftest import FakeResponse
from tools import TOOL_FUNCTIONS
from tools.policy.tool import POLICY_DIR

clarify_tool = TOOL_FUNCTIONS["clarify"]
format_tool = TOOL_FUNCTIONS["format"]
send_tool = TOOL_FUNCTIONS["send"]
lookup_tool = TOOL_FUNCTIONS["lookup"]
fetch_tool = TOOL_FUNCTIONS["fetch"]
timeline_tool = TOOL_FUNCTIONS["timeline"]
social_search_tool = TOOL_FUNCTIONS["social_search"]
policy_tool = TOOL_FUNCTIONS["policy"]


def _set_twitter_env(monkeypatch) -> None:
    monkeypatch.setenv("RAPIDAPI_KEY", "test-rapid-key")
    monkeypatch.setenv("RAPIDAPI_TWITTER_HOST", "twitter-api45.p.rapidapi.com")


def _set_telegram_env(monkeypatch) -> None:
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "123:test-token")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "-1001234567890")


# ---------------- clarify ----------------

def test_clarify_choice_returns_options_and_awaits_user() -> None:
    options = ["Twitter", "Web"]
    result = clarify_tool(question="Bạn muốn tìm ở đâu?", response_type="choice", options=options)

    assert result["options"] == ["Twitter", "Web"]
    assert result["response_type"] == "choice"
    assert result["question"] == "Bạn muốn tìm ở đâu?"
    assert result["awaiting_user"] is True


# ---------------- format ----------------

def test_format_sections_groups_items_by_section() -> None:
    items = [
        {"title": "a1", "url": "https://a.com/1", "section": "A"},
        {"title": "b1", "url": "https://b.com/1", "section": "B"},
        {"title": "a2", "url": "https://a.com/2", "section": "A"},
    ]
    markdown = format_tool(items=items, template="sections")["markdown"]

    assert markdown.count("## A") == 1
    assert markdown.count("## B") == 1
    # a2 is grouped under A, i.e. before the B header.
    assert markdown.index("a2") < markdown.index("## B")


def test_format_thread_numbers_items() -> None:
    items = [{"title": f"t{i}", "url": f"https://x.com/{i}"} for i in range(3)]
    lines = [line for line in format_tool(items=items, template="thread")["markdown"].split("\n\n") if line]

    assert [line.split(" ", 1)[0] for line in lines] == ["1/", "2/", "3/"]
    assert lines[0].startswith("1/ t0")


def test_format_empty_items_does_not_crash() -> None:
    for value in (None, []):
        result = format_tool(items=value, template="sections")
        assert result["item_count"] == 0
        assert result["markdown"] == ""


# ---------------- send (guardrail) ----------------

def test_send_confirmed_posts_to_telegram(monkeypatch, fake_http) -> None:
    _set_telegram_env(monkeypatch)
    calls = fake_http(FakeResponse({"ok": True, "result": {"message_id": 42}}))

    result = send_tool(text="Bản tin AI", confirmed=True)

    assert len(calls) == 1
    assert calls[0]["method"] == "POST"
    assert "bot123:test-token/sendMessage" in calls[0]["url"]
    assert calls[0]["json"]["chat_id"] == "-1001234567890"
    assert calls[0]["json"]["text"] == "Bản tin AI"
    assert result["status"] == "sent"
    assert result["message_id"] == 42


def test_send_confirmed_without_env_returns_error_and_no_request(fake_http) -> None:
    calls = fake_http(FakeResponse({"ok": True}))

    result = send_tool(text="Bản tin", confirmed=True)

    assert calls == []
    assert result["error"] == "RuntimeError"
    assert "TELEGRAM_BOT_TOKEN" in result["message"]


# ---------------- lookup ----------------

def test_lookup_without_timeframe_omits_time_range(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("TAVILY_API_KEY", "test-key")
    calls = fake_http(FakeResponse({"results": []}))

    result = lookup_tool(query="AI", timeframe=None)

    assert "time_range" not in calls[0]["json"]
    assert calls[0]["json"]["query"] == "AI"
    assert result["items"] == []
    assert result["timeframe"] is None


# ---------------- fetch ----------------

def test_fetch_maps_firecrawl_response(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("FIRECRAWL_API_KEY", "fc-test")
    calls = fake_http(FakeResponse({"data": {
        "markdown": "# Hello\nBody",
        "metadata": {"title": "T", "sourceURL": "https://www.example.com/post"},
    }}))

    result = fetch_tool(url="https://www.example.com/post")

    assert calls[0]["url"] == "https://api.firecrawl.dev/v1/scrape"
    assert calls[0]["json"] == {"url": "https://www.example.com/post", "formats": ["markdown"]}
    assert calls[0]["headers"]["Authorization"] == "Bearer fc-test"
    assert result["items"][0] == {
        "title": "T",
        "url": "https://www.example.com/post",
        "source": "example.com",
        "summary": "# Hello\nBody",
    }


def test_fetch_truncates_markdown_to_4000_chars(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("FIRECRAWL_API_KEY", "fc-test")
    fake_http(FakeResponse({"data": {"markdown": "x" * 5000, "metadata": {}}}))

    item = fetch_tool(url="https://example.com")["items"][0]

    assert len(item["summary"]) == 4000
    # Missing metadata falls back to the requested URL.
    assert item["title"] == "https://example.com"
    assert item["url"] == "https://example.com"


# ---------------- timeline / social_search ----------------

def test_timeline_respects_limit_and_skips_items_without_id(monkeypatch, fake_http) -> None:
    _set_twitter_env(monkeypatch)
    raw = [{"text": "no id", "screen_name": "sama"}]
    raw += [{"tweet_id": str(100 + i), "text": f"tweet {i}", "screen_name": "sama"} for i in range(6)]
    calls = fake_http(FakeResponse({"timeline": raw}))

    result = timeline_tool(screenname="sama", limit=3)

    assert calls[0]["params"] == {"screenname": "sama"}
    assert calls[0]["headers"]["x-rapidapi-key"] == "test-rapid-key"
    assert len(result["items"]) == 3
    assert [item["url"] for item in result["items"]] == [
        "https://x.com/sama/status/100",
        "https://x.com/sama/status/101",
        "https://x.com/sama/status/102",
    ]


def test_social_search_passes_search_type(monkeypatch, fake_http) -> None:
    _set_twitter_env(monkeypatch)
    calls = fake_http(FakeResponse({"timeline": [{"tweet_id": "1", "text": "hot", "screen_name": "a"}]}))

    result = social_search_tool(query="GPT-5", search_type="Top", limit=5)

    assert calls[0]["url"] == "https://twitter-api45.p.rapidapi.com/search.php"
    assert calls[0]["params"] == {"query": "GPT-5", "search_type": "Top"}
    assert result["search_type"] == "Top"
    assert result["items"][0]["url"] == "https://x.com/a/status/1"


# ---------------- policy (local knowledge + trust boundary) ----------------

def test_policy_empty_query_returns_no_results() -> None:
    for query in ("", "   ", "the and of"):  # only stopwords -> no search terms
        assert policy_tool(query=query)["results"] == []


def test_policy_area_filter_only_returns_that_area() -> None:
    results = policy_tool(query="data API key transcript", policy_area="data_privacy", top_k=5)["results"]

    assert results, "expected at least one data_privacy hit"
    assert {item["policy_area"] for item in results} == {"data_privacy"}


def test_policy_instruction_like_lines_go_to_untrusted_text() -> None:
    # Find the quoted (">") injection line in the source-citation policy instead of hard-coding it.
    raw = (POLICY_DIR / "source-citation-policy.md").read_text(encoding="utf-8")
    injected = next(line.lstrip("> ").strip() for line in raw.splitlines() if line.startswith(">"))

    results = policy_tool(query="injection probe citation", policy_area="source_citation", top_k=10)["results"]
    probe = next(item for item in results if item["section"] == "Injection probe")

    assert injected in probe["untrusted_text"]
    assert injected not in probe["facts"]
    for item in results:
        assert injected not in item["facts"]


# ---------------- Regression tests: bugs found in existing tools (bonus, group report B5) ----------------

def test_send_string_false_is_not_treated_as_confirmation(monkeypatch, fake_http) -> None:
    # BUG (fixed): `if not confirmed` treated the STRING "false" as truthy and POSTED to Telegram.
    _set_telegram_env(monkeypatch)
    calls = fake_http(FakeResponse({"ok": True}))

    for value in ("false", "False", "no", 1, None):
        assert send_tool(text="Bản tin", confirmed=value)["status"] == "needs_confirmation"
    assert calls == []


def test_send_confirmed_empty_text_returns_error_and_no_request(monkeypatch, fake_http) -> None:
    _set_telegram_env(monkeypatch)
    calls = fake_http(FakeResponse({"ok": True}))

    result = send_tool(text="   ", confirmed=True)

    assert calls == []
    assert result["error"] == "ValueError"


def test_send_retries_as_plain_text_when_markdown_is_rejected(monkeypatch) -> None:
    # Telegram returns 400 for Markdown it cannot parse (e.g. "x.com/some_handle").
    _set_telegram_env(monkeypatch)
    responses = [FakeResponse(status_code=400), FakeResponse({"ok": True, "result": {"message_id": 7}})]
    calls: list[dict[str, Any]] = []

    def _fake_post(url: str, **kwargs: Any) -> FakeResponse:
        calls.append({"url": url, **kwargs})
        return responses.pop(0)

    monkeypatch.setattr(requests, "post", _fake_post)

    result = send_tool(text="Xem https://x.com/some_handle", confirmed=True)

    assert len(calls) == 2
    assert calls[0]["json"]["parse_mode"] == "Markdown"
    assert "parse_mode" not in calls[1]["json"]
    assert result == {"tool": "send_telegram", "status": "sent", "message_id": 7}


def test_send_retries_once_on_connection_reset_then_gives_error_dict(monkeypatch) -> None:
    # Live chat hit ConnectionResetError 10054 twice (transcripts/v3_openrouter_20261111T00*).
    _set_telegram_env(monkeypatch)
    outcomes: list[Any] = [requests.ConnectionError("reset"), FakeResponse({"ok": True, "result": {"message_id": 9}})]
    calls: list[str] = []

    def _fake_post(url: str, **kwargs: Any) -> FakeResponse:
        calls.append(url)
        outcome = outcomes.pop(0)
        if isinstance(outcome, Exception):
            raise outcome
        return outcome

    monkeypatch.setattr(requests, "post", _fake_post)
    assert send_tool(text="Bản tin", confirmed=True)["status"] == "sent"
    assert len(calls) == 2

    # Two resets in a row: stop after 2 attempts and return an error dict (no raise, no 3rd try).
    outcomes[:] = [requests.ConnectionError("reset"), requests.ConnectionError("reset"), FakeResponse({"ok": True})]
    calls.clear()
    result = send_tool(text="Bản tin", confirmed=True)
    assert result["error"] == "ConnectionError"
    assert len(calls) == 2


def test_timeline_strips_at_sign_from_handle(monkeypatch, fake_http) -> None:
    # BUG (fixed): "@sama" was forwarded as-is; the API expects the bare handle.
    _set_twitter_env(monkeypatch)
    calls = fake_http(FakeResponse({"timeline": []}))

    result = timeline_tool(screenname=" @sama ", limit=1)

    assert calls[0]["params"] == {"screenname": "sama"}
    assert result["screenname"] == "sama"


def test_timeline_empty_handle_returns_error_and_no_request(monkeypatch, fake_http) -> None:
    _set_twitter_env(monkeypatch)
    calls = fake_http(FakeResponse({"timeline": []}))

    result = timeline_tool(screenname="@")

    assert calls == []
    assert result["error"] == "ValueError"


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


def test_text_stats_reading_time_rounds_up_per_200_words() -> None:
    assert text_stats_tool(text="từ " * 200)["reading_minutes"] == 1
    assert text_stats_tool(text="từ " * 201)["reading_minutes"] == 2


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


def test_date_diff_wrong_type_returns_error_dict_instead_of_raising() -> None:
    # A model may send a number instead of a string; the tool must not raise.
    result = date_diff_tool(start_date=20261101, end_date="2026-11-15")
    assert result["tool"] == "date_diff"
    assert "error" in result


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


def test_dedupe_by_title_ignores_case_and_extra_spaces() -> None:
    items = [{"title": "OpenAI ra mắt GPT-5"}, {"title": "  openai  RA MẮT gpt-5 "}, {"title": "Tin khác"}]
    result = dedupe_tool(items=items, key="title")
    assert [item["title"] for item in result["items"]] == ["OpenAI ra mắt GPT-5", "Tin khác"]
    assert result["removed_count"] == 1
