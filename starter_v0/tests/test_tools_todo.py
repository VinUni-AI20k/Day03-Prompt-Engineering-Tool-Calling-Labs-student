"""TODO CP3 (student): Tool Unit Test Challenge.

Patterns to copy are in test_tools_examples.py. Fixtures are in conftest.py.

Rules:
- Offline only: mock HTTP with `fake_http`, set fake keys with `monkeypatch.setenv`.
- One behaviour per test. Name the test after the behaviour, not the function.
- Done = `pytest tests/ -v` shows 0 skipped, 0 failed.
"""
from __future__ import annotations

import pytest

from conftest import FakeResponse
from tools import TOOL_FUNCTIONS

TODO = "TODO CP3 (student): implement this test"

clarify = TOOL_FUNCTIONS["clarify"]
format_tool = TOOL_FUNCTIONS["format"]
send = TOOL_FUNCTIONS["send"]
lookup = TOOL_FUNCTIONS["lookup"]
fetch = TOOL_FUNCTIONS["fetch"]
timeline = TOOL_FUNCTIONS["timeline"]
social_search = TOOL_FUNCTIONS["social_search"]
policy = TOOL_FUNCTIONS["policy"]


def _tweet(i: int, handle: str = "sama") -> dict:
    return {"tweet_id": str(1000 + i), "screen_name": handle, "text": f"tweet {i}"}


# ---------------- clarify ----------------

def test_clarify_choice_returns_options_and_awaits_user() -> None:
    result = clarify(question="Chọn nguồn?", response_type="choice", options=["Web", "Twitter"])

    assert result["options"] == ["Web", "Twitter"]
    assert result["response_type"] == "choice"
    assert result["awaiting_user"] is True


# ---------------- format ----------------

def test_format_sections_groups_items_by_section() -> None:
    items = [
        {"title": "a1", "url": "https://x.com/1", "section": "A"},
        {"title": "b1", "url": "https://x.com/2", "section": "B"},
        {"title": "a2", "url": "https://x.com/3", "section": "A"},
    ]
    markdown = format_tool(items=items, template="sections")["markdown"]

    assert markdown.count("## A") == 1
    assert markdown.count("## B") == 1
    assert markdown.index("a2") < markdown.index("## B")


def test_format_thread_numbers_items() -> None:
    items = [{"title": f"t{i}", "url": f"https://e.com/{i}"} for i in range(3)]
    lines = format_tool(items=items, template="thread")["markdown"].split("\n\n")

    assert [line.split(" ")[0] for line in lines] == ["1/", "2/", "3/"]


def test_format_empty_items_does_not_crash() -> None:
    for empty in (None, []):
        result = format_tool(items=empty)
        assert result["item_count"] == 0
        assert "error" not in result


# ---------------- send (guardrail) ----------------

def test_send_confirmed_posts_to_telegram(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "tok123")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "-100999")
    calls = fake_http(FakeResponse({"ok": True}))

    result = send(text="Bản tin AI", confirmed=True)

    assert len(calls) == 1
    assert calls[0]["method"] == "POST"
    assert "bottok123/sendMessage" in calls[0]["url"]
    assert calls[0]["json"]["chat_id"] == "-100999"
    assert calls[0]["json"]["text"] == "Bản tin AI"
    assert result["status"] == "sent"


def test_send_confirmed_without_env_returns_error_and_no_request(fake_http) -> None:
    calls = fake_http(FakeResponse({"ok": True}))

    result = send(text="Bản tin", confirmed=True)

    assert calls == []
    assert result["error"] == "RuntimeError"
    assert "TELEGRAM_BOT_TOKEN" in result["message"]


# ---------------- lookup ----------------

def test_lookup_without_timeframe_omits_time_range(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("TAVILY_API_KEY", "k")
    calls = fake_http(FakeResponse({"results": []}))

    result = lookup(query="AI", timeframe=None)

    assert "time_range" not in calls[0]["json"]
    assert result["timeframe"] is None
    assert result["items"] == []


# ---------------- fetch ----------------

def test_fetch_maps_firecrawl_response(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("FIRECRAWL_API_KEY", "fc")
    calls = fake_http(FakeResponse({"data": {
        "markdown": "# Hello\nbody",
        "metadata": {"title": "T", "sourceURL": "https://www.example.com/post"},
    }}))

    result = fetch(url="https://www.example.com/post")

    assert calls[0]["url"] == "https://api.firecrawl.dev/v1/scrape"
    assert calls[0]["json"]["url"] == "https://www.example.com/post"
    assert result["items"][0] == {
        "title": "T", "url": "https://www.example.com/post",
        "source": "example.com", "summary": "# Hello\nbody",
    }


def test_fetch_truncates_markdown_to_4000_chars(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("FIRECRAWL_API_KEY", "fc")
    fake_http(FakeResponse({"data": {"markdown": "x" * 5000, "metadata": {}}}))

    summary = fetch(url="https://e.com")["items"][0]["summary"]

    assert len(summary) == 4000


# ---------------- timeline / social_search ----------------

def test_timeline_respects_limit_and_skips_items_without_id(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("RAPIDAPI_KEY", "r")
    no_id = {"screen_name": "sama", "text": "no id"}
    calls = fake_http(FakeResponse({"timeline": [no_id] + [_tweet(i) for i in range(6)]}))

    items = timeline(screenname="sama", limit=3)["items"]

    assert calls[0]["params"] == {"screenname": "sama"}
    assert len(items) == 3
    assert [it["url"] for it in items] == [f"https://x.com/sama/status/{1000 + i}" for i in range(3)]


def test_social_search_passes_search_type(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("RAPIDAPI_KEY", "r")
    calls = fake_http(FakeResponse({"timeline": [_tweet(1, "openai")]}))

    result = social_search(query="OpenAI", search_type="Top")

    assert calls[0]["url"].endswith("/search.php")
    assert calls[0]["params"] == {"query": "OpenAI", "search_type": "Top"}
    assert result["search_type"] == "Top"
    assert result["items"][0]["source"] == "@openai"


# ---------------- policy (local knowledge + trust boundary) ----------------

def test_policy_empty_query_returns_no_results() -> None:
    for empty in ("", "   ", "và của"):
        assert policy(query=empty)["results"] == []


def test_policy_area_filter_only_returns_that_area() -> None:
    results = policy(query="dữ liệu cá nhân privacy", policy_area="data_privacy", top_k=10)["results"]

    assert results
    assert {r["policy_area"] for r in results} == {"data_privacy"}


def test_policy_instruction_like_lines_go_to_untrusted_text() -> None:
    results = policy(query="injection probe citation", policy_area="source_citation", top_k=20)["results"]
    probe = next(r for r in results if r["section"] == "Injection probe")

    assert any("ignore the citation policy" in line for line in probe["untrusted_text"])
    assert "ignore the citation policy" not in probe["facts"]
    for r in results:
        assert "ignore the citation policy" not in r["facts"]


# ---------------- regression tests: bugs found in starter tools ----------------
# Bug 1: limit/max_results=0 silently became 5 (`int(x or 5)`).
# Bug 2: policy top_k=0 silently became 1 (`max(1, ...)`).
# Bug 3: clarify(response_type="choice") without options asked a choice with no choices.

@pytest.mark.parametrize("tool_name, kwargs, env", [
    ("timeline", {"screenname": "sama", "limit": 0}, "RAPIDAPI_KEY"),
    ("social_search", {"query": "AI", "limit": -1}, "RAPIDAPI_KEY"),
    ("lookup", {"query": "AI", "max_results": 0}, "TAVILY_API_KEY"),
])
def test_non_positive_limit_returns_error_without_network(monkeypatch, fake_http, tool_name, kwargs, env) -> None:
    monkeypatch.setenv(env, "k")
    calls = fake_http(FakeResponse({"timeline": [_tweet(i) for i in range(6)], "results": []}))

    result = TOOL_FUNCTIONS[tool_name](**kwargs)

    assert result["error"] == "ValueError"
    assert calls == []


def test_limit_none_falls_back_to_default_5(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("RAPIDAPI_KEY", "k")
    fake_http(FakeResponse({"timeline": [_tweet(i) for i in range(8)]}))

    assert len(timeline(screenname="sama", limit=None)["items"]) == 5


def test_limit_numeric_string_from_model_is_accepted(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("TAVILY_API_KEY", "k")
    calls = fake_http(FakeResponse({"results": []}))

    lookup(query="AI", max_results="3")

    assert calls[0]["json"]["max_results"] == 3


def test_policy_top_k_zero_returns_error_dict() -> None:
    result = policy(query="citation", top_k=0)

    assert result["error"] == "ValueError"
    assert "top_k" in result["message"]


def test_clarify_choice_without_options_returns_error() -> None:
    result = clarify(question="Chọn?", response_type="choice", options=[])

    assert result["error"] == "ValueError"
    assert "awaiting_user" not in result


# ---------------- YOUR NEW TOOL(S) ----------------
# Mỗi test kiểm tra MỘT hành vi cụ thể của , tên test mô tả hành vi đó.
# Mọi lời gọi HTTP đều được mock bằng fixture  (conftest.py chặn request thật).

github_search = TOOL_FUNCTIONS["github_search"]


def _repo(name: str, stars: int) -> dict:
    """Dữ liệu giả của 1 repo theo đúng khuôn GitHub REST API trả về."""
    return {
        "full_name": name,
        "html_url": f"https://github.com/{name}",
        "stargazers_count": stars,
        "language": "Python",
        "description": f"Repo {name}",
    }


# 1. Happy path: tham số hợp lệ -> gửi đúng request lên GitHub API VÀ map đúng kết quả trả về.
def test_github_search_sends_query_with_language_and_maps_repos(fake_http) -> None:
    calls = fake_http(FakeResponse({"items": [_repo("openai/swarm", 15000)]}))

    result = github_search(query="agent orchestration", language="python", limit=3)

    assert len(calls) == 1
    assert calls[0]["url"] == "https://api.github.com/search/repositories"
    assert calls[0]["params"]["q"] == "agent orchestration language:python"
    assert calls[0]["params"]["per_page"] == 3
    assert calls[0]["params"]["sort"] == "stars"
    assert "error" not in result
    assert result["items"] == [{
        "title": "openai/swarm",
        "url": "https://github.com/openai/swarm",
        "source": "github.com",
        "stars": 15000,
        "language": "Python",
        "summary": "Repo openai/swarm",
    }]


# 2a. Input xấu từ model: query rỗng hoặc sai kiểu -> trả error dict, KHÔNG gọi mạng.
@pytest.mark.parametrize("bad_query", ["", "   ", None, 123])
def test_github_search_empty_or_wrong_type_query_returns_error_without_request(fake_http, bad_query) -> None:
    calls = fake_http(FakeResponse({"items": []}))

    result = github_search(query=bad_query)

    assert calls == []
    assert result["items"] == []
    assert result["error"].startswith("missing_required_param")
    assert "clarify" in result["next_step"]


# 2b. Input xấu từ model: limit <= 0 -> trả error dict, không gọi mạng.
def test_github_search_non_positive_limit_returns_error_without_request(fake_http) -> None:
    calls = fake_http(FakeResponse({"items": []}))

    result = github_search(query="llm eval", limit=0)

    assert calls == []
    assert result["error"].startswith("invalid_param")


# 2c. Input biên từ model: limit quá lớn hoặc chuỗi số -> ép về khoảng hợp lệ [1, 10].
def test_github_search_clamps_large_limit_and_accepts_numeric_string(fake_http) -> None:
    calls = fake_http(FakeResponse({"items": [_repo(f"o/r{i}", 100 - i) for i in range(15)]}))

    result = github_search(query="rag", limit="999")

    assert calls[0]["params"]["per_page"] == 10
    assert len(result["items"]) == 10


# 3a. Nhánh lỗi API: GitHub trả HTTP 429 (rate limit) -> trả error dict, không raise exception.
def test_github_search_http_429_returns_error_dict(fake_http) -> None:
    fake_http(FakeResponse({"message": "rate limit"}, status_code=429))

    result = github_search(query="rag benchmark", limit=2)

    assert result["items"] == []
    assert "github_api_error" in result["error"]
    assert "429" in result["error"]
    assert "next_step" in result


# 3b. Nhánh lỗi mạng: timeout -> trả error dict, không raise exception.
def test_github_search_network_timeout_returns_error_dict(fake_http) -> None:
    import requests

    fake_http(requests.Timeout("read timed out"))

    result = github_search(query="rag benchmark")

    assert result["items"] == []
    assert "timed out" in result["error"]


# 3c. Nhánh dữ liệu lạ từ API: phần tử hỏng hoặc trường None -> bỏ qua an toàn, không crash.
def test_github_search_malformed_payload_does_not_crash(fake_http) -> None:
    fake_http(FakeResponse({"items": ["not-a-dict", {"full_name": "a/b", "stargazers_count": None, "description": None}]}))

    result = github_search(query="agent")

    assert len(result["items"]) == 1
    assert result["items"][0]["stars"] == 0
    assert result["items"][0]["summary"] == "No description provided."
