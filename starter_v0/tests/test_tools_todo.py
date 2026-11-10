"""

Covers all core/bonus stub tests and >= 3 offline tests per team tool
(Person 2: weather, github_search; Person 3: deduplicate, citation_audit, send guardrail).

Rules:
- Offline only: mock HTTP with `fake_http` or `monkeypatch`, set fake keys with `monkeypatch.setenv`.
- One behaviour per test. Name the test after the behaviour, not the function.
- Done = `pytest tests/ -v` shows 0 skipped, 0 failed.
"""
from __future__ import annotations

from copy import deepcopy

import pytest
import requests

import chat
from agent import ResearchAgent
from conftest import FakeResponse
from providers.base import ModelResponse, ToolCall
from tools import TOOL_FUNCTIONS
from tools.send.tool import approve_message

clarify_tool = TOOL_FUNCTIONS["clarify"]
format_tool = TOOL_FUNCTIONS["format"]
send_tool = TOOL_FUNCTIONS["send"]
lookup_tool = TOOL_FUNCTIONS["lookup"]
fetch_tool = TOOL_FUNCTIONS["fetch"]
timeline_tool = TOOL_FUNCTIONS["timeline"]
social_search_tool = TOOL_FUNCTIONS["social_search"]
policy_tool = TOOL_FUNCTIONS["policy"]
weather_tool = TOOL_FUNCTIONS["weather"]
github_search_tool = TOOL_FUNCTIONS["github_search"]
deduplicate_tool = TOOL_FUNCTIONS["deduplicate"]
citation_audit_tool = TOOL_FUNCTIONS["citation_audit"]


# ---------------- clarify ----------------

def test_clarify_choice_returns_options_and_awaits_user() -> None:
    result = clarify_tool(
        question="Bạn muốn tìm theo nguồn nào?",
        response_type="choice",
        options=["Web", "Twitter"],
    )

    assert result["question"] == "Bạn muốn tìm theo nguồn nào?"
    assert result["response_type"] == "choice"
    assert result["options"] == ["Web", "Twitter"]
    assert result["awaiting_user"] is True


# ---------------- format ----------------

def test_format_sections_groups_items_by_section() -> None:
    items = [
        {"title": "Alpha 1", "url": "https://a.example.com/1", "section": "A"},
        {"title": "Beta 1", "url": "https://b.example.com/1", "section": "B"},
        {"title": "Alpha 2", "url": "https://a.example.com/2", "section": "A"},
    ]
    result = format_tool(items=items, template="sections")
    md = result["markdown"]

    assert result["item_count"] == 3
    assert md.count("## A") == 1
    assert md.count("## B") == 1
    assert md.index("Alpha 2") < md.index("## B")


def test_format_thread_numbers_items() -> None:
    items = [
        {"title": "First", "url": "https://example.com/1"},
        {"title": "Second", "url": "https://example.com/2"},
        {"title": "Third", "url": "https://example.com/3"},
    ]
    result = format_tool(items=items, template="thread")
    chunks = [part for part in result["markdown"].split("\n\n") if part.strip()]

    assert len(chunks) == 3
    assert chunks[0].startswith("1/ ")
    assert chunks[1].startswith("2/ ")
    assert chunks[2].startswith("3/ ")


def test_format_empty_items_does_not_crash() -> None:
    none_result = format_tool(items=None, template="sections")
    empty_result = format_tool(items=[], template="brief")

    assert none_result["item_count"] == 0
    assert isinstance(none_result["markdown"], str)
    assert empty_result["item_count"] == 0
    assert isinstance(empty_result["markdown"], str)


# ---------------- send (guardrail) ----------------

def test_send_confirmed_posts_to_telegram(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "bot-token-123")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "-100987654")
    calls = fake_http(FakeResponse({"ok": True}))

    with approve_message("Bản tin AI sáng nay"):
        result = send_tool(text="Bản tin AI sáng nay", confirmed=True)

    assert len(calls) == 1
    assert calls[0]["method"] == "POST"
    assert "bot-token-123" in calls[0]["url"]
    assert calls[0]["json"] == {"chat_id": "-100987654", "text": "Bản tin AI sáng nay"}
    assert result["status"] == "sent"


def test_send_confirmed_without_env_returns_error_and_no_request(fake_http) -> None:
    calls = fake_http(FakeResponse({"ok": True}))

    with approve_message("Bản tin AI sáng nay"):
        result = send_tool(text="Bản tin AI sáng nay", confirmed=True)

    assert result["error"] == "RuntimeError"
    assert calls == []


# ---------------- lookup ----------------

def test_lookup_without_timeframe_omits_time_range(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("TAVILY_API_KEY", "tvly-fake-key")
    calls = fake_http(FakeResponse({"results": []}))

    result = lookup_tool(query="AI evaluation", topic="general", timeframe=None)

    assert len(calls) == 1
    assert "time_range" not in calls[0]["json"]
    assert result["items"] == []


# ---------------- fetch ----------------

def test_fetch_maps_firecrawl_response(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("FIRECRAWL_API_KEY", "fc-fake-key")
    calls = fake_http(FakeResponse({
        "data": {
            "markdown": "Article content here",
            "metadata": {"title": "T", "sourceURL": "https://example.com/canonical"},
        }
    }))

    result = fetch_tool(url="https://www.example.com/post")

    assert len(calls) == 1
    assert calls[0]["url"] == "https://api.firecrawl.dev/v1/scrape"
    assert calls[0]["json"]["url"] == "https://www.example.com/post"
    assert result["items"] == [{
        "title": "T",
        "url": "https://example.com/canonical",
        "source": "example.com",
        "summary": "Article content here",
    }]


def test_fetch_truncates_markdown_to_4000_chars(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("FIRECRAWL_API_KEY", "fc-fake-key")
    fake_http(FakeResponse({
        "data": {
            "markdown": "x" * 5500,
            "metadata": {"title": "Long", "sourceURL": "https://example.com/long"},
        }
    }))

    result = fetch_tool(url="https://example.com/long")

    assert len(result["items"][0]["summary"]) == 4000
    assert result["items"][0]["summary"] == "x" * 4000


# ---------------- timeline / social_search ----------------

def test_timeline_respects_limit_and_skips_items_without_id(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("RAPIDAPI_KEY", "rapid-fake-key")
    raw_timeline = [{"screen_name": "sama", "text": "missing tweet id"}] + [
        {"tweet_id": str(i), "screen_name": "sama", "text": f"Post {i}"}
        for i in range(6)
    ]
    calls = fake_http(FakeResponse({"timeline": raw_timeline}))

    result = timeline_tool(screenname="sama", limit=3)

    assert len(calls) == 1
    assert calls[0]["method"] == "GET"
    assert calls[0]["params"] == {"screenname": "sama"}
    assert len(result["items"]) == 3
    assert [item["url"] for item in result["items"]] == [
        "https://x.com/sama/status/0",
        "https://x.com/sama/status/1",
        "https://x.com/sama/status/2",
    ]


def test_social_search_passes_search_type(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("RAPIDAPI_KEY", "rapid-fake-key")
    calls = fake_http(FakeResponse({
        "timeline": [
            {"tweet_id": "42", "author": {"screen_name": "openai"}, "text": "Popular tweet"},
        ]
    }))

    result = social_search_tool(query="OpenAI", search_type="Top", limit=4)

    assert len(calls) == 1
    assert calls[0]["params"] == {"query": "OpenAI", "search_type": "Top"}
    assert result["search_type"] == "Top"
    assert result["items"][0]["url"] == "https://x.com/openai/status/42"


# ---------------- policy (local knowledge + trust boundary) ----------------

def test_policy_empty_query_returns_no_results() -> None:
    assert policy_tool(query="")["results"] == []
    assert policy_tool(query="   ")["results"] == []


def test_policy_area_filter_only_returns_that_area() -> None:
    result = policy_tool(query="API key customer data", policy_area="data_privacy", top_k=5)

    assert len(result["results"]) >= 1
    assert all(item["policy_area"] == "data_privacy" for item in result["results"])


def test_policy_instruction_like_lines_go_to_untrusted_text() -> None:
    result = policy_tool(query="injection probe", policy_area="source_citation", top_k=3)

    assert len(result["results"]) >= 1
    hit = result["results"][0]
    assert hit["section"] == "Injection probe"
    assert any("ignore the citation policy" in line for line in hit["untrusted_text"])
    assert "ignore the citation policy" not in hit["facts"]


# ---------------- weather (Person 2) ----------------

def test_weather_happy_path_resolves_capital_and_fetches_forecast(monkeypatch) -> None:
    calls: list[dict] = []

    def fake_get(url: str, **kwargs):
        calls.append({"url": url, **kwargs})
        if "geocoding-api.open-meteo.com" in url:
            return FakeResponse({
                "results": [
                    {
                        "name": "Hanoi",
                        "admin1": "Hanoi",
                        "country": "Vietnam",
                        "country_code": "VN",
                        "latitude": 21.0245,
                        "longitude": 105.8412,
                        "feature_code": "PPLC",
                    },
                    {
                        "name": "Hanoi Airport",
                        "country_code": "VN",
                        "latitude": 21.2212,
                        "longitude": 105.8072,
                        "feature_code": "AIRP",
                    },
                ]
            })
        return FakeResponse({
            "timezone": "Asia/Bangkok",
            "current_units": {"temperature_2m": "°C"},
            "current": {
                "time": "2026-11-10T12:00",
                "temperature_2m": 26.5,
                "apparent_temperature": 27.1,
                "relative_humidity_2m": 68,
                "weather_code": 1,
                "wind_speed_10m": 11.4,
            },
        })

    monkeypatch.setattr(requests, "get", fake_get)
    result = weather_tool(location="Hanoi", country_code="vn", units="celsius")

    assert len(calls) == 2
    assert calls[0]["params"]["name"] == "Hanoi"
    assert calls[0]["params"]["countryCode"] == "VN"
    assert calls[1]["params"]["latitude"] == 21.0245
    assert calls[1]["params"]["temperature_unit"] == "celsius"
    assert result["condition"] == "Ít mây"
    assert result["location"]["feature_code"] == "PPLC"
    assert result["items"][0]["source"] == "Open-Meteo"
    assert "26.5 °C" in result["items"][0]["summary"]


def test_weather_ambiguous_location_returns_candidates_without_forecast(fake_http) -> None:
    calls = fake_http(FakeResponse({
        "results": [
            {"name": "Springfield", "admin1": "Illinois", "country": "United States",
             "country_code": "US", "latitude": 39.8, "longitude": -89.6, "feature_code": "PPLA"},
            {"name": "Springfield", "admin1": "Missouri", "country": "United States",
             "country_code": "US", "latitude": 37.2, "longitude": -93.3, "feature_code": "PPLA2"},
        ]
    }))

    result = weather_tool(location="Springfield")

    assert len(calls) == 1
    assert result["error"] == "ambiguous_location"
    assert len(result["candidates"]) == 2
    assert result["items"] == []


def test_weather_location_not_found_returns_error_without_forecast(fake_http) -> None:
    calls = fake_http(FakeResponse({"results": []}))

    result = weather_tool(location="AtlantisCity")

    assert len(calls) == 1
    assert result["error"] == "location_not_found"
    assert result["items"] == []


@pytest.mark.parametrize("kwargs", [
    {"location": ""},
    {"location": "A"},
    {"location": "Hanoi", "country_code": "VNM"},
    {"location": "Hanoi", "units": "kelvin"},
])
def test_weather_bad_input_returns_error_without_network(fake_http, kwargs) -> None:
    calls = fake_http(FakeResponse({"results": []}))

    result = weather_tool(**kwargs)

    assert result["error"] == "ValueError"
    assert result["items"] == []
    assert calls == []


@pytest.mark.parametrize("response,expected_error", [
    (FakeResponse(status_code=503), "HTTPError"),
    (requests.Timeout("Open-Meteo timed out"), "Timeout"),
])
def test_weather_failure_returns_error_dict(fake_http, response, expected_error) -> None:
    fake_http(response)

    result = weather_tool(location="Hanoi")

    assert result["error"] == expected_error
    assert result["items"] == []


def test_weather_fahrenheit_resolves_accented_city_and_formats_imperial(monkeypatch) -> None:
    calls: list[dict] = []

    def fake_get(url: str, **kwargs):
        calls.append({"url": url, **kwargs})
        if "geocoding-api.open-meteo.com" in url:
            return FakeResponse({
                "results": [
                    {
                        "name": "Hanoi",
                        "admin1": "Hanoi",
                        "country": "Vietnam",
                        "country_code": "VN",
                        "latitude": 21.0245,
                        "longitude": 105.8412,
                        "feature_code": "PPLC",
                    }
                ]
            })
        return FakeResponse({
            "timezone": "Asia/Bangkok",
            "current": {
                "time": "2026-11-10T15:00",
                "temperature_2m": 79.7,
                "apparent_temperature": 81.0,
                "relative_humidity_2m": 65,
                "weather_code": 0,
                "wind_speed_10m": 8.2,
            },
        })

    monkeypatch.setattr(requests, "get", fake_get)
    result = weather_tool(location="Hà Nội, Vietnam", units="fahrenheit")

    assert len(calls) == 2
    assert calls[0]["params"]["name"] == "Hà Nội, Vietnam"
    assert calls[1]["params"]["temperature_unit"] == "fahrenheit"
    assert result["units"] == "fahrenheit"
    assert "79.7 °F" in result["items"][0]["summary"]
    assert "temperature_unit=fahrenheit" in result["items"][0]["url"]


def test_weather_incomplete_forecast_payload_returns_value_error(monkeypatch) -> None:
    def fake_get(url: str, **kwargs):
        if "geocoding-api.open-meteo.com" in url:
            return FakeResponse({
                "results": [
                    {
                        "name": "Tokyo",
                        "country_code": "JP",
                        "latitude": 35.6895,
                        "longitude": 139.6917,
                        "feature_code": "PPLC",
                    }
                ]
            })
        return FakeResponse({"current": {"time": "2026-11-10T15:00", "temperature_2m": 15.0}})

    monkeypatch.setattr(requests, "get", fake_get)
    result = weather_tool(location="Tokyo")

    assert result["error"] == "ValueError"
    assert result["items"] == []


# ---------------- github_search (Person 2) ----------------

def test_github_search_happy_path_maps_public_repos_and_omits_best_match_sort(fake_http) -> None:
    calls = fake_http(FakeResponse({
        "total_count": 2,
        "incomplete_results": False,
        "items": [
            {
                "full_name": "secret/private-repo",
                "html_url": "https://github.com/secret/private-repo",
                "private": True,
            },
            {
                "full_name": "langchain-ai/langchain",
                "html_url": "https://github.com/langchain-ai/langchain",
                "private": False,
                "description": "Build context-aware reasoning applications",
                "stargazers_count": 100000,
                "forks_count": 16000,
                "language": "Python",
                "license": {"spdx_id": "MIT"},
                "topics": ["rag", "llm"],
                "archived": False,
                "updated_at": "2026-11-09T10:00:00Z",
            },
        ],
    }))

    result = github_search_tool(query="RAG language:Python", sort="best_match", order="desc", max_results=3)

    assert len(calls) == 1
    assert calls[0]["url"] == "https://api.github.com/search/repositories"
    assert calls[0]["params"] == {"q": "RAG language:Python is:public", "per_page": 3, "order": "desc"}
    assert "sort" not in calls[0]["params"]
    assert len(result["items"]) == 1
    assert result["items"][0]["title"] == "langchain-ai/langchain"
    assert result["items"][0]["source"] == "github.com"
    assert result["items"][0]["license"] == "MIT"


def test_github_search_passes_sort_order_and_optional_token(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("GITHUB_TOKEN", "ghp-fake-token")
    calls = fake_http(FakeResponse({"total_count": 0, "incomplete_results": False, "items": []}))

    result = github_search_tool(query="fastapi", sort="stars", order="asc", max_results=2)

    assert len(calls) == 1
    assert calls[0]["params"]["sort"] == "stars"
    assert calls[0]["params"]["order"] == "asc"
    assert calls[0]["headers"]["Authorization"] == "Bearer ghp-fake-token"
    assert result["items"] == []


def test_github_search_skips_incomplete_entries_and_truncates_to_max_results(fake_http) -> None:
    fake_http(FakeResponse({
        "total_count": 4,
        "incomplete_results": False,
        "items": [
            {"full_name": "missing/url", "private": False},
            {"html_url": "https://github.com/missing/name", "private": False},
            {"full_name": "org/repo-1", "html_url": "https://github.com/org/repo-1", "description": None, "license": None},
            {"full_name": "org/repo-2", "html_url": "https://github.com/org/repo-2", "description": "Second", "license": {"spdx_id": "Apache-2.0"}},
        ],
    }))

    result = github_search_tool(query="agent", max_results=1)

    assert len(result["items"]) == 1
    assert result["items"][0]["title"] == "org/repo-1"
    assert result["items"][0]["summary"] == "Không có mô tả."
    assert result["items"][0]["license"] is None


@pytest.mark.parametrize("kwargs", [
    {"query": ""},
    {"query": "   "},
    {"query": "rag", "sort": "newest"},
    {"query": "rag", "order": "random"},
    {"query": "rag", "max_results": "5"},
    {"query": "rag", "max_results": 2.5},
    {"query": "rag", "max_results": True},
    {"query": "rag", "max_results": 0},
    {"query": "rag", "max_results": 11},
])
def test_github_search_bad_input_returns_error_without_network(fake_http, kwargs) -> None:
    calls = fake_http(FakeResponse({"items": []}))

    result = github_search_tool(**kwargs)

    assert result["error"] == "ValueError"
    assert result["items"] == []
    assert calls == []


@pytest.mark.parametrize("response,expected_error", [
    (FakeResponse(status_code=403), "HTTPError"),
    (requests.Timeout("GitHub timeout"), "Timeout"),
    (FakeResponse({"items": "invalid"}), "ValueError"),
])
def test_github_search_failure_returns_error_dict(fake_http, response, expected_error) -> None:
    fake_http(response)

    result = github_search_tool(query="ai agent")

    assert result["error"] == expected_error
    assert result["items"] == []


# ---------------- deduplicate (Person 3) ----------------

def test_deduplicate_normalizes_tracking_params_and_preserves_order() -> None:
    items = [
        {"title": "First", "url": "https://example.com/news?b=2&a=1&utm_source=x"},
        {"title": "Duplicate", "url": "https://EXAMPLE.com/news?a=1&gclid=abc&b=2&fbclid=99#top"},
        {"title": "HttpVariant", "url": "http://example.com/news?a=1&b=2"},
    ]
    snapshot = deepcopy(items)

    result = deduplicate_tool(items=items)

    assert result["input_count"] == 3
    assert result["removed_count"] == 1
    assert result["items"] == [items[0], items[2]]
    assert items == snapshot


@pytest.mark.parametrize("bad_items", [
    None,
    "not-a-list",
    [1],
    [{"title": "missing url"}],
    [{"url": "ftp://example.com/file"}],
    [{"url": "https://user:pass@example.com"}],
    [{"url": "https://example.com:bad"}],
    [{"url": "https://example.com"}] * 101,
])
def test_deduplicate_bad_input_returns_error_dict(bad_items) -> None:
    result = deduplicate_tool(items=bad_items)

    assert result["error"] == "ValueError"


def test_deduplicate_empty_list_returns_zero_removed() -> None:
    result = deduplicate_tool(items=[])

    assert result["items"] == []
    assert result["input_count"] == 0
    assert result["removed_count"] == 0


# ---------------- citation_audit (Person 3) ----------------

def test_citation_audit_valid_unique_items_passes() -> None:
    items = [
        {"title": "Attention Is All You Need", "source": "arxiv.org", "url": "https://arxiv.org/abs/1706.03762"},
        {"title": "OpenAI Research", "source": "openai.com", "url": "https://openai.com/research/"},
    ]

    result = citation_audit_tool(items=items)

    assert result["passed"] is True
    assert result["issues"] == []
    assert result["item_count"] == 2
    assert "Metadata only" in result["scope"]


def test_citation_audit_empty_list_passes_local_metadata_check() -> None:
    result = citation_audit_tool(items=[])

    assert result["passed"] is True
    assert result["item_count"] == 0
    assert result["issues"] == []


def test_citation_audit_reports_missing_invalid_and_duplicate_fields() -> None:
    items = [
        {"title": "Valid", "source": "example.com", "url": "https://example.com/a"},
        {"title": "Dup", "source": "example.com", "url": "https://example.com/a?gclid=1#sec"},
        {"title": "", "url": "javascript:alert(1)"},
        {"title": "BlankURL", "source": "example.com", "url": "   "},
    ]

    result = citation_audit_tool(items=items)

    assert result["passed"] is False
    assert result["issues"] == [
        {"index": 1, "problems": ["duplicate_url"]},
        {"index": 2, "problems": ["missing_title", "missing_source", "invalid_url"]},
        {"index": 3, "problems": ["missing_url"]},
    ]


@pytest.mark.parametrize("bad_items", [None, "bad", [123], [{}] * 101])
def test_citation_audit_bad_collection_returns_error_dict(bad_items) -> None:
    result = citation_audit_tool(items=bad_items)

    assert result["error"] == "ValueError"


# ---------------- send guardrail (Person 3) ----------------

def test_approve_message_is_not_registered_as_model_tool() -> None:
    assert "approve_message" not in TOOL_FUNCTIONS


def test_send_confirmed_without_host_approval_returns_needs_confirmation(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "bot-token-123")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "-100987654")
    calls = fake_http(FakeResponse({"ok": True}))

    result = send_tool(text="Unapproved message", confirmed=True)

    assert result["status"] == "needs_confirmation"
    assert calls == []


@pytest.mark.parametrize("confirmed_value", [False, "true", "false", 1])
def test_send_rejects_non_boolean_confirmed_even_with_host_approval(monkeypatch, fake_http, confirmed_value) -> None:
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "bot-token-123")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "-100987654")
    calls = fake_http(FakeResponse({"ok": True}))

    with approve_message("Tin nhắn thử"):
        result = send_tool(text="Tin nhắn thử", confirmed=confirmed_value)

    assert result["status"] == "needs_confirmation"
    assert calls == []


def test_send_approval_binds_exact_text_and_is_single_use(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "bot-token-123")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "-100987654")
    calls = fake_http(FakeResponse({"ok": True}))

    with approve_message("Tin nhắn gốc"):
        modified = send_tool(text="Tin nhắn bị chỉnh sửa", confirmed=True)
        first = send_tool(text="Tin nhắn gốc", confirmed=True)
        replay = send_tool(text="Tin nhắn gốc", confirmed=True)

    after_exit = send_tool(text="Tin nhắn gốc", confirmed=True)

    assert modified["status"] == "needs_confirmation"
    assert first["status"] == "sent"
    assert replay["status"] == "needs_confirmation"
    assert after_exit["status"] == "needs_confirmation"
    assert len(calls) == 1


def test_send_consumes_approval_even_when_attempt_fails(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "bot-token-123")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "-100987654")
    fake_http(FakeResponse(status_code=500))

    with approve_message("Tin nhắn lỗi"):
        failed = send_tool(text="Tin nhắn lỗi", confirmed=True)
        retry = send_tool(text="Tin nhắn lỗi", confirmed=True)

    assert failed["error"] == "HTTPError"
    assert retry["status"] == "needs_confirmation"


@pytest.mark.parametrize("bad_text", ["", "   ", "a" * 4097])
def test_send_approved_rejects_empty_or_overlong_text_without_network(monkeypatch, fake_http, bad_text) -> None:
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "bot-token-123")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "-100987654")
    calls = fake_http(FakeResponse({"ok": True}))

    with approve_message(bad_text):
        result = send_tool(text=bad_text, confirmed=True)

    assert result["error"] == "ValueError"
    assert calls == []


@pytest.mark.parametrize("response", [
    FakeResponse({"ok": False}),
    FakeResponse(status_code=500),
    requests.Timeout("https://api.telegram.org/botSUPERSECRET/sendMessage"),
])
def test_send_failure_returns_sanitized_error_without_token(monkeypatch, fake_http, response) -> None:
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "SUPERSECRET")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "-100987654")
    fake_http(response)

    with approve_message("Tin nhắn thử nghiệm"):
        result = send_tool(text="Tin nhắn thử nghiệm", confirmed=True)

    assert "error" in result
    assert "SUPERSECRET" not in str(result)


def test_agent_send_guardrail_fails_closed_even_when_model_sets_confirmed_true(monkeypatch, fake_http) -> None:
    class _FakeSendProvider:
        def complete(self, messages, tools=None, *, model=None, temperature=0.0, tool_choice=None) -> ModelResponse:
            return ModelResponse(text=None, tool_calls=[ToolCall("send", {"text": "Tự động gửi", "confirmed": True})])

    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "bot-token-123")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "-100987654")
    calls = fake_http(FakeResponse({"ok": True}))

    run = ResearchAgent(_FakeSendProvider(), system_prompt="test").run([{"role": "user", "content": "Gửi lên Telegram"}])

    assert run.tool_results[0]["result"]["status"] == "needs_confirmation"
    assert calls == []


@pytest.mark.parametrize("answer,expected_status,expected_calls", [
    ("SEND", "sent", 1),
    ("send", "cancelled", 0),
    ("yes", "cancelled", 0),
    ("", "cancelled", 0),
])
def test_cli_execute_tool_call_send_requires_exact_SEND_token(monkeypatch, fake_http, answer, expected_status, expected_calls) -> None:
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "bot-token-123")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "-100987654")
    monkeypatch.setattr("builtins.input", lambda _: answer)
    calls = fake_http(FakeResponse({"ok": True}))

    event = chat.execute_tool_call(ToolCall("send", {"text": "Chào nhóm", "confirmed": True}))

    assert event["result"]["status"] == expected_status
    assert len(calls) == expected_calls


def test_cli_execute_tool_call_send_eof_cancels_without_network(monkeypatch, fake_http) -> None:
    def _raise_eof(_prompt: str) -> str:
        raise EOFError()

    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "bot-token-123")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "-100987654")
    monkeypatch.setattr("builtins.input", _raise_eof)
    calls = fake_http(FakeResponse({"ok": True}))

    event = chat.execute_tool_call(ToolCall("send", {"text": "Chào nhóm", "confirmed": True}))

    assert event["result"]["status"] == "cancelled"
    assert calls == []
