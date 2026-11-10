"""Mocked Tavily / Firecrawl / Twitter API45 tests; zero billable calls."""
import requests
import pytest

from tools.topic_radar.tool import compare_topic_signals


class Response:
    def __init__(self, data=None, error=None):
        self.data = data or {}
        self.error = error

    def raise_for_status(self):
        if self.error:
            raise self.error

    def json(self):
        return self.data


@pytest.fixture(autouse=True)
def credentials(monkeypatch):
    monkeypatch.setenv("TAVILY_API_KEY", "fake-tavily")
    monkeypatch.setenv("RAPIDAPI_KEY", "fake-rapid")
    monkeypatch.delenv("FIRECRAWL_API_KEY", raising=False)
    monkeypatch.delenv("RAPIDAPI_TWITTER_HOST", raising=False)


def news():
    return {"results": [
        {"url": "https://abc.org/solar", "title": "Solar research updates", "content": "Solar research update"},
        {"url": "https://abc.org/solar", "title": "duplicate", "content": "Solar research update"},
        {"url": "https://def.org/grid", "title": "Grid development", "content": "Solar grid research"},
    ]}


def social():
    return {"timeline": [
        {"tweet_id": "123", "screen_name": "researcher", "text": "Solar research looks promising", "favorites": 10},
        {"tweet_id": "123", "screen_name": "researcher", "text": "duplicate"},
        {"tweet_id": "124", "author": {"screen_name": "scientist"}, "text": "Solar grid news"},
    ]}


def test_merge_sources_and_cross_platform_terms(monkeypatch):
    monkeypatch.setattr("tools.topic_radar.tool.requests.post", lambda *a, **k: Response(news()))
    monkeypatch.setattr("tools.topic_radar.tool.requests.get", lambda *a, **k: Response(social()))
    result = compare_topic_signals("solar research", limit=5)
    assert result["status"] == "ok"
    assert result["signals"]["news_results"] == 2
    assert result["signals"]["x_post_results"] == 2
    assert result["signals"]["news_domains"] == 2
    assert "solar" in result["signals"]["shared_terms"]
    assert len(result["items"]) == 4
    assert any(item["url"] == "https://x.com/researcher/status/123" for item in result["items"])


def test_news_only_never_calls_rapidapi(monkeypatch):
    monkeypatch.setattr("tools.topic_radar.tool.requests.post", lambda *a, **k: Response(news()))
    monkeypatch.setattr("tools.topic_radar.tool.requests.get", lambda *a, **k: pytest.fail("unexpected RapidAPI call"))
    result = compare_topic_signals("solar", include_social=False)
    assert result["status"] == "ok"
    assert result["signals"]["x_post_results"] == 0


def test_missing_rapidapi_key_degrades_gracefully(monkeypatch):
    monkeypatch.delenv("RAPIDAPI_KEY")
    monkeypatch.setattr("tools.topic_radar.tool.requests.post", lambda *a, **k: Response(news()))
    result = compare_topic_signals("solar")
    assert result["status"] == "partial"
    assert result["signals"]["news_results"] == 2
    assert any("RapidAPI" in issue for issue in result["warnings"])


def test_tavily_error_keeps_social(monkeypatch):
    monkeypatch.setattr("tools.topic_radar.tool.requests.post", lambda *a, **k: Response(error=requests.HTTPError("503")))
    monkeypatch.setattr("tools.topic_radar.tool.requests.get", lambda *a, **k: Response(social()))
    result = compare_topic_signals("solar")
    assert result["status"] == "partial"
    assert result["signals"]["news_results"] == 0
    assert result["signals"]["x_post_results"] == 2


def test_both_provider_errors_returns_error(monkeypatch):
    monkeypatch.delenv("TAVILY_API_KEY")
    monkeypatch.delenv("RAPIDAPI_KEY")
    result = compare_topic_signals("solar")
    assert result["tool"] == "topic_radar"
    assert result["error"] == "RuntimeError"


def test_enrich_top_two_and_cap(monkeypatch):
    monkeypatch.setenv("FIRECRAWL_API_KEY", "fake-fc")
    calls = []
    def post(url, **kwargs):
        calls.append(url)
        if url.endswith("/search"):
            return Response(news())
        assert url.endswith("/v2/scrape")
        return Response({"success": True, "data": {"markdown": "# Detailed research article with extra facts"}})
    monkeypatch.setattr("tools.topic_radar.tool.requests.post", post)
    result = compare_topic_signals("solar", include_social=False, enrich_articles=True)
    assert sum(url.endswith("/v2/scrape") for url in calls) == 2
    assert all(i["provider"] == "firecrawl" for i in result["items"])


def test_enrich_falls_back_to_tavily_extract(monkeypatch):
    monkeypatch.setenv("FIRECRAWL_API_KEY", "fake-fc")
    def post(url, **kwargs):
        if url.endswith("/search"):
            return Response({"results": [news()["results"][0]]})
        if "firecrawl.dev" in url:
            return Response(error=requests.HTTPError("503"))
        assert url.endswith("/extract")
        return Response({"results": [{"raw_content": "Original article body from Tavily Extract"}]})
    monkeypatch.setattr("tools.topic_radar.tool.requests.post", post)
    result = compare_topic_signals("solar", include_social=False, enrich_articles=True)
    assert result["items"][0]["provider"] == "tavily_extract"


@pytest.mark.parametrize("kwargs", [
    {"query": ""}, {"query": "x" * 251},
    {"query": "solar", "timeframe": "decade"},
    {"query": "solar", "limit": 11},
    {"query": "solar", "limit": True},
    {"query": "solar", "include_social": 1},
    {"query": "solar", "enrich_articles": "yes"},
])
def test_invalid_arguments_no_network(monkeypatch, kwargs):
    monkeypatch.setattr("tools.topic_radar.tool.requests.post", lambda *a, **k: pytest.fail("unexpected HTTP"))
    assert compare_topic_signals(**kwargs)["error"] == "ValueError"


def test_rejects_bad_rapidapi_host_but_retains_news(monkeypatch):
    monkeypatch.setenv("RAPIDAPI_TWITTER_HOST", "localhost")
    monkeypatch.setattr("tools.topic_radar.tool.requests.post", lambda *a, **k: Response(news()))
    result = compare_topic_signals("solar")
    assert result["status"] == "partial"
    assert result["signals"]["news_results"] == 2


def test_malformed_news_url_skipped(monkeypatch):
    monkeypatch.setattr("tools.topic_radar.tool.requests.post", lambda *a, **k: Response({"results": [
        {"url": "javascript:alert(1)", "title": "bad"},
        {"url": "https://example.com/news", "content": "solar report"},
    ]}))
    result = compare_topic_signals("solar", include_social=False)
    assert len(result["items"]) == 1
    assert result["items"][0]["source"] == "example.com"
