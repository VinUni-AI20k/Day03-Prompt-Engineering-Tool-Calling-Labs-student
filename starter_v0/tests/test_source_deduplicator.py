"""Unit tests for source_deduplicator (no real network or paid API calls)."""
from __future__ import annotations

import requests

from conftest import FakeResponse
from tools.source_deduplicator.tool import deduplicate_sources


def test_deduplicates_tracking_url_without_api(fake_http) -> None:
    calls = fake_http(FakeResponse({}))
    items = [
        {"title": "Một tiêu đề", "url": "https://www.a.com/news?id=2"},
        {"title": "Một tiêu đề", "url": "https://a.com/news?utm_source=x&id=2#top"},
        {"title": "Tin khác", "url": "https://b.com/other"},
    ]
    result = deduplicate_sources(items)
    assert result["removed"] == 1
    assert result["items"] == [items[0], items[2]]
    assert calls == []


def test_deduplicates_similar_title_without_api() -> None:
    result = deduplicate_sources([
        {"url": "https://a.com/1", "title": "OpenAI introduces new tools for research agents today"},
        {"url": "https://b.com/2", "title": "OpenAI introduces new tools for research agents today!"},
    ])
    assert result["removed"] == 1


def test_bad_input_returns_error_not_exception() -> None:
    assert deduplicate_sources({"url": "https://a.com"})["error"] == "ValueError"
    assert deduplicate_sources([{"url": "file:///etc/passwd"}])["error"] == "ValueError"
    assert deduplicate_sources([], verify_content="true")["error"] == "ValueError"


def test_verification_uses_firecrawl_when_available(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("FIRECRAWL_API_KEY", "fake-firecrawl-key")
    text = " ".join(f"researchword{i}" for i in range(60))
    calls = fake_http(FakeResponse({"data": {"markdown": text}}))
    result = deduplicate_sources([
        {"url": "https://a.com/1", "title": "First title"},
        {"url": "https://b.com/2", "title": "Different title"},
    ], verify_content=True)
    assert result["removed"] == 1
    assert result["verification"] == "content"
    assert len(calls) == 2
    assert all(call["url"] == "https://api.firecrawl.dev/v2/scrape" for call in calls)


def test_verification_falls_back_to_tavily(monkeypatch) -> None:
    monkeypatch.setenv("FIRECRAWL_API_KEY", "fake-fc")
    monkeypatch.setenv("TAVILY_API_KEY", "fake-tv")
    calls = []

    def post(url, **kwargs):
        calls.append(url)
        if "firecrawl" in url:
            return FakeResponse(status_code=502)
        return FakeResponse({"results": [{"raw_content": "Research article " * 20}]})

    monkeypatch.setattr(requests, "post", post)
    result = deduplicate_sources([{"url": "https://a.com/1", "title": "Article A"}], verify_content=True)
    assert result["removed"] == 0
    assert calls == ["https://api.firecrawl.dev/v2/scrape", "https://api.tavily.com/extract"]


def test_api_failure_returns_error_dict(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("FIRECRAWL_API_KEY", "fake")
    calls = fake_http(FakeResponse(status_code=503))
    result = deduplicate_sources([{"url": "https://a.com/1"}], verify_content=True)
    assert result["error"] == "RuntimeError"
    assert len(calls) == 1


def test_missing_api_key_returns_error_without_http(fake_http) -> None:
    calls = fake_http(FakeResponse({}))
    result = deduplicate_sources([{"url": "https://a.com/1"}], verify_content=True)
    assert result["error"] == "RuntimeError"
    assert calls == []
