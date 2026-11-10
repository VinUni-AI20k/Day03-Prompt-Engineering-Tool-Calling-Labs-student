"""CP3: Tool unit tests (Step 4b).

Patterns are copied from test_tools_examples.py. Fixtures are in conftest.py.

Rules:
- Offline only: mock HTTP with `fake_http`, set fake keys with `monkeypatch.setenv`.
- One behaviour per test. Name the test after the behaviour, not the function.
- Assert both the REQUEST we send and the RESULT we return.
"""
from __future__ import annotations

import re

import pytest
import requests

from conftest import FakeResponse
from tools import TOOL_FUNCTIONS
from tools._shared import fold_text

clarify_tool = TOOL_FUNCTIONS["clarify"]
format_tool = TOOL_FUNCTIONS["format"]
send_tool = TOOL_FUNCTIONS["send"]
lookup_tool = TOOL_FUNCTIONS["lookup"]
fetch_tool = TOOL_FUNCTIONS["fetch"]
timeline_tool = TOOL_FUNCTIONS["timeline"]
social_search_tool = TOOL_FUNCTIONS["social_search"]
policy_tool = TOOL_FUNCTIONS["policy"]
wiki_tool = TOOL_FUNCTIONS["wiki"]


# ---------------- clarify ----------------

def test_clarify_choice_returns_options_and_awaits_user() -> None:
    options = ["@sama", "@karpathy"]
    result = clarify_tool(question="Bạn muốn xem tài khoản nào?", response_type="choice", options=options)

    assert result["options"] == ["@sama", "@karpathy"]
    assert result["response_type"] == "choice"
    assert result["question"] == "Bạn muốn xem tài khoản nào?"
    assert result["awaiting_user"] is True


# ---------------- format ----------------

def test_format_sections_groups_items_by_section() -> None:
    items = [
        {"title": "a1", "url": "https://a.com/1", "section": "A"},
        {"title": "b1", "url": "https://b.com/1", "section": "B"},
        {"title": "a2", "url": "https://a.com/2", "section": "A"},
    ]
    result = format_tool(items=items, template="sections", headline="Digest")
    lines = result["markdown"].splitlines()

    assert lines[0] == "# Digest"
    assert lines.count("## A") == 1
    assert lines.count("## B") == 1
    # a1 và a2 nằm chung dưới "## A", trước "## B"
    assert lines.index("## A") < lines.index("- a2 - [a.com](https://a.com/2)") < lines.index("## B")
    assert result["item_count"] == 3


def test_format_thread_numbers_items() -> None:
    items = [{"title": f"Tin {i}", "url": f"https://x.com/{i}"} for i in range(3)]
    result = format_tool(items=items, template="thread")
    posts = result["markdown"].split("\n\n")

    assert [post.split(" ", 1)[0] for post in posts] == ["1/", "2/", "3/"]
    assert posts[0] == "1/ Tin 0 - [x.com](https://x.com/0)"


@pytest.mark.parametrize("empty", [None, []])
@pytest.mark.parametrize("template", ["brief", "sections", "bullets", "thread", "daily_ai_vn"])
def test_format_empty_items_does_not_crash(empty, template) -> None:
    result = format_tool(items=empty, template=template)

    assert result["item_count"] == 0
    assert isinstance(result["markdown"], str)


# ---------------- send (guardrail) ----------------

def test_send_confirmed_posts_to_telegram(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "123:test-token")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "-100999")
    calls = fake_http(FakeResponse({"ok": True}))

    result = send_tool(text="Bản tin AI", confirmed=True)

    assert len(calls) == 1
    assert calls[0]["method"] == "POST"
    assert calls[0]["url"] == "https://api.telegram.org/bot123:test-token/sendMessage"
    assert calls[0]["json"]["chat_id"] == "-100999"
    assert calls[0]["json"]["text"] == "Bản tin AI"
    assert result == {"tool": "send_telegram", "status": "sent"}


def test_send_confirmed_without_env_returns_error_and_no_request(fake_http) -> None:
    calls = fake_http(FakeResponse({"ok": True}))

    result = send_tool(text="Bản tin AI", confirmed=True)

    assert calls == []
    assert result["error"] == "RuntimeError"
    assert "TELEGRAM_BOT_TOKEN" in result["message"]
    assert result.get("status") != "sent"


# ---------------- lookup ----------------

def test_lookup_without_timeframe_omits_time_range(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("TAVILY_API_KEY", "test-key")
    calls = fake_http(FakeResponse({"results": []}))

    result = lookup_tool(query="AI", topic="general", timeframe=None)

    assert "time_range" not in calls[0]["json"]
    assert calls[0]["json"]["query"] == "AI"
    assert calls[0]["json"]["topic"] == "general"
    assert result["timeframe"] is None
    assert result["items"] == []


# ---------------- fetch ----------------

def test_fetch_maps_firecrawl_response(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("FIRECRAWL_API_KEY", "fc-test")
    calls = fake_http(FakeResponse({"data": {
        "markdown": "# Hello\nBody text",
        "metadata": {"title": "T", "sourceURL": "https://www.example.com/post?ref=1"},
    }}))

    result = fetch_tool(url="https://www.example.com/post")

    assert calls[0]["method"] == "POST"
    assert calls[0]["url"] == "https://api.firecrawl.dev/v1/scrape"
    assert calls[0]["json"] == {"url": "https://www.example.com/post", "formats": ["markdown"]}
    assert calls[0]["headers"]["Authorization"] == "Bearer fc-test"
    assert result["items"][0] == {
        "title": "T",
        "url": "https://www.example.com/post?ref=1",
        "source": "example.com",
        "summary": "# Hello\nBody text",
    }


def test_fetch_truncates_markdown_to_4000_chars(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("FIRECRAWL_API_KEY", "fc-test")
    fake_http(FakeResponse({"data": {"markdown": "a" * 3999 + "b" + "c" * 2000, "metadata": {}}}))

    result = fetch_tool(url="https://example.com/long")
    summary = result["items"][0]["summary"]

    assert len(summary) == 4000
    assert summary.endswith("b")
    assert "c" not in summary
    # metadata rỗng -> fallback về chính URL
    assert result["items"][0]["title"] == "https://example.com/long"


# ---------------- timeline / social_search ----------------

def test_timeline_respects_limit_and_skips_items_without_id(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("RAPIDAPI_KEY", "rk-test")
    raw = [{"text": "no id", "screen_name": "sama"}]
    raw += [{"tweet_id": str(100 + i), "text": f"tweet {i}", "screen_name": "sama"} for i in range(6)]
    calls = fake_http(FakeResponse({"timeline": raw}))

    result = timeline_tool(screenname="sama", limit=3)

    assert calls[0]["url"] == "https://twitter-api45.p.rapidapi.com/timeline.php"
    assert calls[0]["params"] == {"screenname": "sama"}
    assert calls[0]["headers"]["x-rapidapi-key"] == "rk-test"
    assert len(result["items"]) == 3
    assert [item["summary"] for item in result["items"]] == ["tweet 0", "tweet 1", "tweet 2"]
    for item in result["items"]:
        assert re.fullmatch(r"https://x\.com/sama/status/\d+", item["url"])


@pytest.mark.parametrize("search_type", ["Top", "Latest"])
def test_social_search_passes_search_type(monkeypatch, fake_http, search_type) -> None:
    monkeypatch.setenv("RAPIDAPI_KEY", "rk-test")
    calls = fake_http(FakeResponse({"timeline": [{"tweet_id": "1", "text": "hi", "screen_name": "a"}]}))

    result = social_search_tool(query="GPT-5", search_type=search_type, limit=5)

    assert calls[0]["url"] == "https://twitter-api45.p.rapidapi.com/search.php"
    assert calls[0]["params"] == {"query": "GPT-5", "search_type": search_type}
    assert result["search_type"] == search_type
    assert result["items"][0]["url"] == "https://x.com/a/status/1"


# ---------------- policy (local knowledge + trust boundary) ----------------

@pytest.mark.parametrize("query", ["", "   ", "?!"])
def test_policy_empty_query_returns_no_results(query) -> None:
    result = policy_tool(query=query)

    assert result["results"] == []
    assert "error" not in result


def test_policy_area_filter_only_returns_that_area() -> None:
    result = policy_tool(query="API key customer data confidential", policy_area="data_privacy", top_k=5)

    assert result["results"], "data_privacy policy should match this query"
    assert {hit["policy_area"] for hit in result["results"]} == {"data_privacy"}
    assert len(result["results"]) <= 5


def test_policy_instruction_like_lines_go_to_untrusted_text() -> None:
    result = policy_tool(query="injection probe citation", policy_area="source_citation", top_k=10)
    hits = result["results"]

    probe = [hit for hit in hits if hit["section"] == "Injection probe"]
    assert probe, "the Injection probe section should be retrieved"
    untrusted = probe[0]["untrusted_text"]
    assert any("ignore" in fold_text(line) for line in untrusted)
    # Dòng giống lệnh KHÔNG được lọt vào facts của bất kỳ section nào.
    for hit in hits:
        for line in untrusted:
            assert line not in hit["facts"]
        assert "ignore" not in fold_text(hit["facts"])
    assert "untrusted" in result["trust_boundary"]


# ---------------- wiki (tool mới của nhóm) ----------------
# 1. happy path (mocked)  2. input xấu từ model  3. nhánh lỗi -> error dict, không raise

WIKI_PAYLOAD = {"query": {"pages": [
    # API trả pages không theo thứ tự relevance; "index" mới là thứ hạng.
    {"pageid": 2, "index": 2, "title": "Attention (machine learning)",
     "fullurl": "https://en.wikipedia.org/wiki/Attention_(machine_learning)",
     "extract": "Attention is a technique."},
    {"pageid": 1, "index": 1, "title": "Transformer (deep learning)",
     "fullurl": "https://en.wikipedia.org/wiki/Transformer_(deep_learning)",
     "extract": "A transformer is a deep learning\narchitecture."},
]}}


def test_wiki_sends_search_request_and_maps_pages_in_rank_order(fake_http) -> None:
    calls = fake_http(FakeResponse(WIKI_PAYLOAD))

    result = wiki_tool(query="  Transformer   deep learning ", lang="en", max_results=2)

    assert len(calls) == 1
    assert calls[0]["method"] == "GET"
    assert calls[0]["url"] == "https://en.wikipedia.org/w/api.php"
    assert calls[0]["params"]["gsrsearch"] == "Transformer deep learning"
    assert calls[0]["params"]["gsrlimit"] == 2
    assert calls[0]["params"]["explaintext"] == 1
    assert "User-Agent" in calls[0]["headers"]
    assert [item["title"] for item in result["items"]] == ["Transformer (deep learning)", "Attention (machine learning)"]
    assert result["items"][0] == {
        "title": "Transformer (deep learning)",
        "url": "https://en.wikipedia.org/wiki/Transformer_(deep_learning)",
        "source": "en.wikipedia.org",
        "summary": "A transformer is a deep learning architecture.",
        "pageid": 1,
    }
    assert result["item_count"] == 2


def test_wiki_empty_query_returns_error_without_request(fake_http) -> None:
    calls = fake_http(FakeResponse(WIKI_PAYLOAD))

    for bad_query in ["", "   ", None]:
        result = wiki_tool(query=bad_query)
        assert result["error"] == "ValueError"
        assert "query" in result["message"]
    assert calls == []


def test_wiki_normalizes_bad_lang_and_max_results_from_model(fake_http) -> None:
    calls = fake_http(FakeResponse(WIKI_PAYLOAD))

    wiki_tool(query="GPT", lang="french", max_results="2")   # ngoài enum, số dạng chuỗi
    wiki_tool(query="GPT", lang="VI", max_results=100)       # viết hoa, vượt trần
    wiki_tool(query="GPT", max_results=0)                    # dưới sàn
    wiki_tool(query="GPT", max_results="abc")                # không phải số

    assert calls[0]["url"] == "https://en.wikipedia.org/w/api.php"
    assert calls[0]["params"]["gsrlimit"] == 2
    assert calls[1]["url"] == "https://vi.wikipedia.org/w/api.php"
    assert calls[1]["params"]["gsrlimit"] == 5
    assert calls[2]["params"]["gsrlimit"] == 1
    assert calls[3]["params"]["gsrlimit"] == 3


def test_wiki_no_results_returns_empty_items(fake_http) -> None:
    fake_http(FakeResponse({"batchcomplete": True}))  # API không có key "query" khi không tìm thấy

    result = wiki_tool(query="xqzzv nonexistent")

    assert result["items"] == []
    assert result["item_count"] == 0
    assert "error" not in result


def test_wiki_http_error_returns_error_dict(fake_http) -> None:
    fake_http(FakeResponse(status_code=503))

    result = wiki_tool(query="GPT")

    assert result["tool"] == "wiki_search"
    assert result["error"] == "HTTPError"
    assert "503" in result["message"]


def test_wiki_api_error_payload_returns_error_dict(fake_http) -> None:
    fake_http(FakeResponse({"error": {"code": "badvalue", "info": "Unrecognized value"}}))

    result = wiki_tool(query="GPT")

    assert result["error"] == "RuntimeError"
    assert "Unrecognized value" in result["message"]


def test_wiki_timeout_returns_error_dict(fake_http) -> None:
    fake_http(requests.Timeout("read timed out"))

    result = wiki_tool(query="GPT")

    assert result["error"] == "Timeout"
