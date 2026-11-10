"""Tool Unit Test Challenge (Completed for CP3 by NguyenHoangTrung).

All tests run strictly OFFLINE:
- HTTP requests are mocked with `fake_http`.
- Environment variables are isolated via `monkeypatch`.
- Zero skipped, zero failed test suite.
"""

from __future__ import annotations
from conftest import FakeResponse
from tools import TOOL_FUNCTIONS


# ---------------- clarify ----------------

def test_clarify_choice_returns_options_and_awaits_user() -> None:
    clarify_tool = TOOL_FUNCTIONS["clarify"]
    result = clarify_tool(question="Ban muon doc theo dinh dang nao?", response_type="choice", options=["brief", "bullets"])

    assert result["tool"] == "ask_user"
    assert result["question"] == "Ban muon doc theo dinh dang nao?"
    assert result["response_type"] == "choice"
    assert result["options"] == ["brief", "bullets"]
    assert result["awaiting_user"] is True


# ---------------- format ----------------

def test_format_sections_groups_items_by_section() -> None:
    format_tool = TOOL_FUNCTIONS["format"]
    items = [
        {"title": "Bai 1", "url": "https://example.com/1", "section": "A"},
        {"title": "Bai 2", "url": "https://example.com/2", "section": "B"},
        {"title": "Bai 3", "url": "https://example.com/3", "section": "A"},
    ]
    result = format_tool(items=items, template="sections")
    md = result["markdown"]

    assert md.count("## A") == 1
    assert md.count("## B") == 1
    assert result["item_count"] == 3


def test_format_thread_numbers_items() -> None:
    format_tool = TOOL_FUNCTIONS["format"]
    items = [
        {"title": "Item 1", "url": "https://example.com/1"},
        {"title": "Item 2", "url": "https://example.com/2"},
        {"title": "Item 3", "url": "https://example.com/3"},
    ]
    result = format_tool(items=items, template="thread")
    paragraphs = [p.strip() for p in result["markdown"].split("\n\n") if p.strip()]

    assert len(paragraphs) == 3
    assert paragraphs[0].startswith("1/ ")
    assert paragraphs[1].startswith("2/ ")
    assert paragraphs[2].startswith("3/ ")


def test_format_empty_items_does_not_crash() -> None:
    format_tool = TOOL_FUNCTIONS["format"]
    res_none = format_tool(items=None)
    assert res_none["item_count"] == 0
    assert res_none["markdown"] == ""

    res_empty = format_tool(items=[])
    assert res_empty["item_count"] == 0
    assert res_empty["markdown"] == ""


# ---------------- send (guardrail) ----------------

def test_send_confirmed_posts_to_telegram(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "-1001234567890")
    calls = fake_http(FakeResponse({"ok": True, "result": {"message_id": 999}}))

    send_tool = TOOL_FUNCTIONS["send"]
    result = send_tool(text="Ban tin AI sang", confirmed=True)

    assert len(calls) == 1
    assert "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11" in calls[0]["url"]
    assert calls[0]["json"]["chat_id"] == "-1001234567890"
    assert calls[0]["json"]["text"] == "Ban tin AI sang"
    assert result["status"] == "sent"


def test_send_confirmed_without_env_returns_error_and_no_request(fake_http) -> None:
    calls = fake_http(FakeResponse({"ok": True}))
    send_tool = TOOL_FUNCTIONS["send"]
    result = send_tool(text="Bản tin", confirmed=True)

    assert calls == []
    assert result["error"] == "RuntimeError"
    assert "TELEGRAM_BOT_TOKEN" in result["message"]


# ---------------- lookup ----------------

def test_lookup_without_timeframe_omits_time_range(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("TAVILY_API_KEY", "test-tavily-key")
    calls = fake_http(FakeResponse({"results": []}))

    lookup_tool = TOOL_FUNCTIONS["lookup"]
    result = lookup_tool(query="DeepSeek model", timeframe=None)

    assert len(calls) == 1
    assert "time_range" not in calls[0]["json"]
    assert calls[0]["json"]["query"] == "DeepSeek model"
    assert result["tool"] == "web_search"


# ---------------- fetch ----------------

def test_fetch_maps_firecrawl_response(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("FIRECRAWL_API_KEY", "test-firecrawl-key")
    calls = fake_http(FakeResponse({
        "data": {
            "markdown": "Detailed research content on frontier LLMs.",
            "metadata": {
                "title": "Frontier AI Safety",
                "sourceURL": "https://openai.com/research/frontier-safety",
            },
        }
    }))

    fetch_tool = TOOL_FUNCTIONS["fetch"]
    result = fetch_tool(url="https://openai.com/research/frontier-safety")

    assert len(calls) == 1
    assert len(result["items"]) == 1
    item = result["items"][0]
    assert item["title"] == "Frontier AI Safety"
    assert item["url"] == "https://openai.com/research/frontier-safety"
    assert item["source"] == "openai.com"
    assert item["summary"] == "Detailed research content on frontier LLMs."


def test_fetch_truncates_markdown_to_4000_chars(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("FIRECRAWL_API_KEY", "test-firecrawl-key")
    huge_markdown = "A" * 7500
    fake_http(FakeResponse({
        "data": {
            "markdown": huge_markdown,
            "metadata": {"title": "Huge Document", "sourceURL": "https://example.com/huge"},
        }
    }))

    fetch_tool = TOOL_FUNCTIONS["fetch"]
    result = fetch_tool(url="https://example.com/huge")

    assert len(result["items"][0]["summary"]) == 4000
    assert result["items"][0]["summary"] == "A" * 4000


# ---------------- timeline / social_search ----------------

def test_timeline_respects_limit_and_skips_items_without_id(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("RAPIDAPI_KEY", "test-rapid-key")
    raw_tweets = [
        {"text": "Invalid tweet with no ID"},
        {"tweet_id": "1001", "screen_name": "sama", "text": "Tweet 1"},
        {"id": "1002", "screen_name": "sama", "text": "Tweet 2"},
        {"tweet_id": "1003", "screen_name": "sama", "text": "Tweet 3"},
        {"tweet_id": "1004", "screen_name": "sama", "text": "Tweet 4"},
        {"tweet_id": "1005", "screen_name": "sama", "text": "Tweet 5"},
        {"tweet_id": "1006", "screen_name": "sama", "text": "Tweet 6"},
    ]
    fake_http(FakeResponse({"timeline": raw_tweets}))

    timeline_tool = TOOL_FUNCTIONS["timeline"]
    result = timeline_tool(screenname="sama", limit=3)

    assert len(result["items"]) == 3
    for item in result["items"]:
        assert item["url"].startswith("https://x.com/sama/status/")
    assert result["items"][0]["title"] == "Tweet 1"
    assert result["items"][1]["title"] == "Tweet 2"
    assert result["items"][2]["title"] == "Tweet 3"


def test_social_search_passes_search_type(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("RAPIDAPI_KEY", "test-rapid-key")
    calls = fake_http(FakeResponse({"timeline": []}))

    social_search_tool = TOOL_FUNCTIONS["social_search"]
    social_search_tool(query="Gemini 3.8", search_type="Top", limit=7)

    assert len(calls) == 1
    assert calls[0]["params"]["query"] == "Gemini 3.8"
    assert calls[0]["params"]["search_type"] == "Top"


# ---------------- policy (local knowledge + trust boundary) ----------------

def test_policy_empty_query_returns_no_results() -> None:
    policy_tool = TOOL_FUNCTIONS["policy"]
    result = policy_tool(query="", policy_area="all")
    assert result["results"] == []


def test_policy_area_filter_only_returns_that_area() -> None:
    policy_tool = TOOL_FUNCTIONS["policy"]
    result = policy_tool(query="customer data privacy secrets", policy_area="data_privacy")

    assert len(result["results"]) > 0
    for hit in result["results"]:
        assert hit["policy_area"] == "data_privacy"


def test_policy_instruction_like_lines_go_to_untrusted_text() -> None:
    policy_tool = TOOL_FUNCTIONS["policy"]
    result = policy_tool(query="injection probe", policy_area="source_citation")

    injection_hits = [h for h in result["results"] if h["section"] == "Injection probe"]
    assert len(injection_hits) > 0
    target_hit = injection_hits[0]

    assert any("ignore the citation policy" in line for line in target_hit["untrusted_text"])
    assert "ignore the citation policy" not in target_hit["facts"]


# ---------------- YOUR NEW TOOL(S): source_credibility ----------------

def test_my_new_tool_happy_path() -> None:
    """Happy path: check academic URL returns highest tier and verified credibility."""
    credibility_tool = TOOL_FUNCTIONS["source_credibility"]
    result = credibility_tool(url="https://arxiv.org/abs/2401.12345", min_tier="academic")

    assert result["tool"] == "source_credibility"
    assert result["domain"] == "arxiv.org"
    assert result["tier"] == "academic"
    assert result["score"] >= 0.90
    assert result["meets_min_tier"] is True
    assert result["is_reliable"] is True
    assert "Highly credible source" in result["recommendation"]

def test_text_stats_failure_invalid_wpm_returns_error_dict() -> None:
    res_zero = TOOL_FUNCTIONS["text_stats"](text="Hello world", wpm=0)
    assert res_zero["status"] == "error"
    assert "error" in res_zero

def test_my_new_tool_bad_input_from_model() -> None:
    """Bad / missing input handling: model sends empty string, non-string, or invalid URL."""
    credibility_tool = TOOL_FUNCTIONS["source_credibility"]

    res_empty = credibility_tool(url="")
    assert res_empty["tool"] == "source_credibility"
    assert res_empty["error"] == "ValueError"
    assert "URL string must be provided" in res_empty["message"]

    res_whitespace = credibility_tool(url="   ")
    assert res_whitespace["error"] == "ValueError"

    res_none = credibility_tool(url=None)  # type: ignore[arg-type]
    assert res_none["error"] == "ValueError"


def test_my_new_tool_failure_returns_error_dict(monkeypatch) -> None:
    """Failure path: internal exception is safely caught and mapped to error dict, never raises."""
    credibility_tool = TOOL_FUNCTIONS["source_credibility"]
    import tools.source_credibility.tool as sc_module

    def _broken_domain(_: str) -> str:
        raise RuntimeError("Simulated DNS socket failure")

    monkeypatch.setattr(sc_module, "domain", _broken_domain)
    result = credibility_tool(url="https://example.com/test")

    assert isinstance(result, dict)
    assert result["tool"] == "source_credibility"
    assert result["error"] == "RuntimeError"
    assert "Simulated DNS socket failure" in result["message"]


def test_my_new_tool_unverified_domain_marked_unreliable() -> None:
    """Verify unknown / unverified sources receive low trust score and require caution."""
    credibility_tool = TOOL_FUNCTIONS["source_credibility"]
    result = credibility_tool(url="https://unverified-crypto-leak.xyz/article/1")

    assert result["domain"] == "unverified-crypto-leak.xyz"
    assert result["tier"] == "unverified"
    assert result["score"] <= 0.40
    assert result["is_reliable"] is False
    assert "Unverified source" in result["recommendation"]


def test_my_new_tool_min_tier_filtering() -> None:
    """Verify filtering when source tier falls below the required threshold."""
    credibility_tool = TOOL_FUNCTIONS["source_credibility"]
    result = credibility_tool(url="https://x.com/elonmusk/status/123456", min_tier="verified_news")

    assert result["domain"] == "x.com"
    assert result["tier"] == "community"
    assert result["meets_min_tier"] is False
    assert result["is_reliable"] is False
