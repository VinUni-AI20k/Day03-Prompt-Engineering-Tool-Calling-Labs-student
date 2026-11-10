"""Tool Unit Test Challenge (filled in by NhomNoName).

Rules:
- Offline only: mock HTTP with `fake_http`, set fake keys with `monkeypatch.setenv`.
- One behaviour per test. Name the test after the behaviour, not the function.
- Done = `pytest tests/ -v` shows 0 skipped, 0 failed.
"""
from __future__ import annotations

import re

import requests

from conftest import FakeResponse
from tools import TOOL_FUNCTIONS

clarify_tool = TOOL_FUNCTIONS["clarify"]
format_tool = TOOL_FUNCTIONS["format"]
send_tool = TOOL_FUNCTIONS["send"]
lookup_tool = TOOL_FUNCTIONS["lookup"]
fetch_tool = TOOL_FUNCTIONS["fetch"]
timeline_tool = TOOL_FUNCTIONS["timeline"]
social_search_tool = TOOL_FUNCTIONS["social_search"]
policy_tool = TOOL_FUNCTIONS["policy"]
web_answer_tool = TOOL_FUNCTIONS["web_answer"]


# ---------------- clarify ----------------

def test_clarify_choice_returns_options_and_awaits_user() -> None:
    options = ["Sam Altman", "Elon Musk"]
    result = clarify_tool(question="Bạn muốn xem tài khoản nào?", response_type="choice", options=options)

    assert result["options"] == options
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
    # both A items sit under the single A heading, before B
    assert markdown.index("a1") < markdown.index("a2") < markdown.index("## B")


def test_format_thread_numbers_items() -> None:
    items = [{"title": f"Tin {i}"} for i in range(3)]
    markdown = format_tool(items=items, template="thread")["markdown"]

    lines = [line for line in markdown.split("\n") if line.strip()]
    assert [line.split(" ", 1)[0] for line in lines] == ["1/", "2/", "3/"]


def test_format_empty_items_does_not_crash() -> None:
    for empty in (None, []):
        result = format_tool(items=empty, template="sections")
        assert result["item_count"] == 0


# ---------------- send (guardrail) ----------------

def test_send_confirmed_posts_to_telegram(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "123:fake-token")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "42")
    calls = fake_http(FakeResponse({"ok": True}))

    result = send_tool(text="Bản tin AI", confirmed=True)

    assert len(calls) == 1
    assert calls[0]["method"] == "POST"
    assert "123:fake-token" in calls[0]["url"]
    assert calls[0]["json"]["chat_id"] == "42"
    assert calls[0]["json"]["text"] == "Bản tin AI"
    assert result["status"] == "sent"


def test_send_confirmed_without_env_returns_error_and_no_request(fake_http) -> None:
    calls = fake_http(FakeResponse({"ok": True}))

    result = send_tool(text="Bản tin AI", confirmed=True)

    assert result["error"] == "RuntimeError"
    assert "TELEGRAM_BOT_TOKEN" in result["message"]
    assert calls == []


# ---------------- lookup ----------------

def test_lookup_without_timeframe_omits_time_range(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("TAVILY_API_KEY", "test-key")
    calls = fake_http(FakeResponse({"results": []}))

    lookup_tool(query="AI", topic="news", timeframe=None)

    assert "time_range" not in calls[0]["json"]


# ---------------- fetch ----------------

def test_fetch_maps_firecrawl_response(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("FIRECRAWL_API_KEY", "test-key")
    fake_http(FakeResponse({"data": {
        "markdown": "Nội dung bài viết",
        "metadata": {"title": "T", "sourceURL": "https://www.example.com/post"},
    }}))

    item = fetch_tool(url="https://www.example.com/post")["items"][0]

    assert item == {
        "title": "T",
        "url": "https://www.example.com/post",
        "source": "example.com",
        "summary": "Nội dung bài viết",
    }


def test_fetch_truncates_markdown_to_4000_chars(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("FIRECRAWL_API_KEY", "test-key")
    fake_http(FakeResponse({"data": {"markdown": "x" * 5000, "metadata": {}}}))

    summary = fetch_tool(url="https://example.com")["items"][0]["summary"]

    assert len(summary) == 4000


# ---------------- timeline / social_search ----------------

def test_timeline_respects_limit_and_skips_items_without_id(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("RAPIDAPI_KEY", "test-key")
    raw = [{"text": "no id", "screen_name": "sama"}]
    raw += [{"tweet_id": str(1000 + i), "text": f"tweet {i}", "screen_name": "sama"} for i in range(6)]
    fake_http(FakeResponse({"timeline": raw}))

    items = timeline_tool(screenname="sama", limit=3)["items"]

    assert len(items) == 3
    assert all(re.fullmatch(r"https://x\.com/sama/status/\d+", item["url"]) for item in items)
    assert "no id" not in [item["summary"] for item in items]


def test_social_search_passes_search_type(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("RAPIDAPI_KEY", "test-key")
    calls = fake_http(FakeResponse({"timeline": []}))

    for search_type in ("Top", "Latest"):
        social_search_tool(query="cybersecurity", search_type=search_type)

    assert [call["params"] for call in calls] == [
        {"query": "cybersecurity", "search_type": "Top"},
        {"query": "cybersecurity", "search_type": "Latest"},
    ]


# ---------------- policy (local knowledge + trust boundary) ----------------

def test_policy_empty_query_returns_no_results() -> None:
    for empty in ("", "   ", "?!"):
        assert policy_tool(query=empty)["results"] == []


def test_policy_area_filter_only_returns_that_area() -> None:
    results = policy_tool(query="data privacy customer", policy_area="data_privacy", top_k=10)["results"]

    assert results
    assert all(item["policy_area"] == "data_privacy" for item in results)


def test_policy_instruction_like_lines_go_to_untrusted_text() -> None:
    results = policy_tool(query="injection probe", policy_area="source_citation", top_k=5)["results"]
    probe = next(item for item in results if item["section"] == "Injection probe")

    assert any("ignore the citation policy" in line for line in probe["untrusted_text"])
    assert "ignore" not in probe["facts"].lower()


def test_policy_vietnamese_query_with_area_still_returns_that_area() -> None:
    # Bug found in live chat (transcript 20261110T141305): the policy docs are written in English,
    # so the model's Vietnamese query "trích dẫn nguồn" matched 0 keywords and the agent told the
    # user "no citation policy exists". The eval case G04 still PASSED because it only grades args.
    results = policy_tool(query="trích dẫn nguồn", policy_area="source_citation", top_k=3)["results"]

    assert results
    assert all(item["policy_area"] == "source_citation" for item in results)


# ---------------- YOUR NEW TOOL(S): web_answer ----------------
# (5 more web_answer tests live in tests/test_web_answer.py)

def test_my_new_tool_happy_path(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("TAVILY_API_KEY", "test-key")
    calls = fake_http(FakeResponse({
        "answer": "RAG kết hợp truy xuất tài liệu với mô hình sinh.",
        "results": [{"title": "RAG", "url": "https://www.example.com/rag", "content": "RAG...", "score": 0.9}],
    }))

    result = web_answer_tool(question="  RAG là gì?  ", max_results=3)

    body = calls[0]["json"]
    assert body["query"] == "RAG là gì?"  # question is stripped before sending
    assert body["topic"] == "general"
    assert body["include_answer"]
    assert result["answer_source"] == "tavily_answer"
    assert result["items"][0]["source"] == "example.com"
    # only one source behind the answer -> must not claim medium confidence
    assert result["confidence"] == "low"


def test_my_new_tool_bad_input_from_model(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("TAVILY_API_KEY", "test-key")
    calls = fake_http(FakeResponse({"results": []}))

    blank = web_answer_tool(question="   ")
    wrong_type = web_answer_tool(question="RAG là gì?", max_results="nhiều")

    assert blank["error"] == "ValueError"
    assert wrong_type["error"] == "ValueError"
    assert calls == []  # bad input never reaches the paid API


def test_my_new_tool_failure_returns_error_dict(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("TAVILY_API_KEY", "test-key")

    fake_http(FakeResponse(status_code=500))
    assert web_answer_tool(question="RAG là gì?")["error"] == "HTTPError"

    fake_http(requests.Timeout("timed out"))
    assert web_answer_tool(question="RAG là gì?")["error"] == "Timeout"
