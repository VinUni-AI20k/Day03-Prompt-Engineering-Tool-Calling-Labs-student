"""Mocked API contract tests; no real API calls/credits."""
import requests
import pytest

from tools.evidence_finder.tool import find_claim_evidence


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
    monkeypatch.delenv("FIRECRAWL_API_KEY", raising=False)


def test_unique_domains_and_normalized_structure(monkeypatch):
    def post(url, **kwargs):
        assert url.endswith("/search")
        return Response({"results": [
            {"url": "https://a.com/one", "title": "Solar panel costs fall", "content": "Solar panel costs fell this year."},
            {"url": "https://a.com/two", "title": "Repost", "content": "Same publisher"},
            {"url": "https://b.com/three", "title": "Other", "content": "Solar costs report."},
        ]})
    monkeypatch.setattr("tools.evidence_finder.tool.requests.post", post)
    result = find_claim_evidence("Solar panel costs fall", max_sources=3, deep_read=False)
    assert result["status"] == "ok"
    assert result["distinct_domains"] == 2
    assert {i["source"] for i in result["items"]} == {"a.com", "b.com"}
    assert all(i["extraction_provider"] == "search_snippet" for i in result["items"])
    assert result["assessment"] == "requires_review"


def test_firecrawl_deep_read(monkeypatch):
    monkeypatch.setenv("FIRECRAWL_API_KEY", "fake-fc")
    calls = []
    def post(url, **kwargs):
        calls.append(url)
        if url.endswith("/search"):
            return Response({"results": [{"url": "https://a.com/article", "title": "Article", "content": "Tiny"}]})
        if url.endswith("/v2/scrape"):
            return Response({"success": True, "data": {"markdown": "Solar panel costs fell significantly this year according to report data."}})
        raise AssertionError(url)
    monkeypatch.setattr("tools.evidence_finder.tool.requests.post", post)
    result = find_claim_evidence("Solar panel costs fell", deep_read=True)
    assert result["items"][0]["extraction_provider"] == "firecrawl"
    assert "significantly" in result["items"][0]["summary"]
    assert any("/v2/scrape" in url for url in calls)


def test_firecrawl_failure_uses_tavily_extract(monkeypatch):
    monkeypatch.setenv("FIRECRAWL_API_KEY", "fake-fc")
    def post(url, **kwargs):
        if url.endswith("/search"):
            return Response({"results": [{"url": "https://news.org/story", "title": "News", "content": "Short"}]})
        if "firecrawl.dev" in url:
            return Response(error=requests.HTTPError("503"))
        if url.endswith("/extract"):
            return Response({"results": [{"raw_content": "Updated observation reported by different independent researchers today in official report."}]})
        raise AssertionError(url)
    monkeypatch.setattr("tools.evidence_finder.tool.requests.post", post)
    result = find_claim_evidence("updated observation reported")
    assert result["items"][0]["extraction_provider"] == "tavily_extract"
    assert "Firecrawl" in " ".join(result["warnings"])


def test_tavily_extract_without_firecrawl_key(monkeypatch):
    def post(url, **kwargs):
        if url.endswith("/search"):
            return Response({"results": [{"url": "https://news.org/story", "content": "Short"}]})
        assert url.endswith("/extract")
        return Response({"results": [{"raw_content": "Updated observation reported by different independent researchers today in official report."}]})
    monkeypatch.setattr("tools.evidence_finder.tool.requests.post", post)
    assert find_claim_evidence("updated observation reported")["items"][0]["extraction_provider"] == "tavily_extract"


def test_missing_key_returns_error(monkeypatch):
    monkeypatch.delenv("TAVILY_API_KEY")
    result = find_claim_evidence("Solar panel costs fall")
    assert result["tool"] == "evidence_finder"
    assert result["error"] == "RuntimeError"


@pytest.mark.parametrize("kwargs", [
    {"claim": "  "}, {"claim": "x" * 351}, {"claim": None},
    {"claim": "Solar panels", "max_sources": 0},
    {"claim": "Solar panels", "max_sources": True},
    {"claim": "Solar panels", "deep_read": "false"},
])
def test_invalid_input_without_http(monkeypatch, kwargs):
    monkeypatch.setattr("tools.evidence_finder.tool.requests.post", lambda *a, **k: pytest.fail("unexpected HTTP"))
    assert find_claim_evidence(**kwargs)["error"] == "ValueError"


def test_rejects_internal_and_malformed_urls(monkeypatch):
    monkeypatch.setattr("tools.evidence_finder.tool.requests.post", lambda *a, **k: Response({"results": [
        {"url": "http://127.0.0.1:8080/private", "title": "private"},
        {"url": "ftp://docs.com/x", "title": "ftp"},
        {"url": "https://example.org/story", "title": "public", "content": "Solar panel costs fell"},
    ]}))
    result = find_claim_evidence("Solar panel costs", deep_read=False)
    assert len(result["items"]) == 1
    assert result["items"][0]["source"] == "example.org"


def test_empty_results(monkeypatch):
    monkeypatch.setattr("tools.evidence_finder.tool.requests.post", lambda *a, **k: Response({"results": []}))
    result = find_claim_evidence("Solar panel costs", deep_read=False)
    assert result["status"] == "no_results"
    assert result["items"] == []


def test_both_extractors_fail_keeps_snippet(monkeypatch):
    monkeypatch.setenv("FIRECRAWL_API_KEY", "fake-fc")
    def post(url, **kwargs):
        if url.endswith("/search"):
            return Response({"results": [{"url": "https://example.org/a", "content": "Solar costs research report"}]})
        return Response(error=requests.HTTPError("503"))
    monkeypatch.setattr("tools.evidence_finder.tool.requests.post", post)
    result = find_claim_evidence("Solar costs research report", deep_read=True)
    assert result["items"][0]["summary"] == "Solar costs research report"
    assert result["items"][0]["extraction_provider"] == "search_snippet"
    assert len(result["warnings"]) == 2
