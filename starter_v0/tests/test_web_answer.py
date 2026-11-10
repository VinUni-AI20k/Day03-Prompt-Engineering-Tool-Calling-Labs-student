"""Unit tests for the team's fallback tool `web_answer` (Tavily is mocked — no network, no API cost)."""
from __future__ import annotations

from typing import Any

import pytest

from tools.web_answer import tool as web_answer_tool
from tools.web_answer.tool import answer_from_web


class _FakeResponse:
    def __init__(self, payload: dict[str, Any]) -> None:
        self._payload = payload

    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict[str, Any]:
        return self._payload


@pytest.fixture
def capture_post(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("TAVILY_API_KEY", "test-key")
    calls: list[dict[str, Any]] = []

    def install(payload: dict[str, Any]) -> list[dict[str, Any]]:
        def fake_post(url: str, json: dict[str, Any], headers: dict[str, str], timeout: int) -> _FakeResponse:
            calls.append({"url": url, "json": json, "headers": headers})
            return _FakeResponse(payload)

        monkeypatch.setattr(web_answer_tool.requests, "post", fake_post)
        return calls

    return install


RESULTS = [
    {"title": "RAG explained", "url": "https://www.example.com/rag", "content": "RAG combines retrieval with generation. It reduces hallucination.", "score": 0.9},
    {"title": "What is RAG", "url": "https://docs.other.org/rag", "content": "Retrieval-augmented generation fetches documents first. Then the LLM answers.", "score": 0.8},
]


def test_returns_tavily_answer_with_sources(capture_post) -> None:
    calls = capture_post({"answer": "RAG là kỹ thuật kết hợp truy xuất tài liệu với sinh văn bản.", "results": RESULTS})
    out = answer_from_web(question="RAG là gì?")
    assert out["answer"].startswith("RAG là kỹ thuật")
    assert out["answer_source"] == "tavily_answer"
    assert out["confidence"] == "medium"
    assert [i["source"] for i in out["items"]] == ["example.com", "docs.other.org"]
    sent = calls[0]["json"]
    assert sent["query"] == "RAG là gì?" and sent["include_answer"] and sent["topic"] == "general"


def test_falls_back_to_snippets_when_no_answer(capture_post) -> None:
    capture_post({"answer": None, "results": RESULTS})
    out = answer_from_web(question="RAG là gì?")
    assert out["answer_source"] == "top_snippets"
    assert out["confidence"] == "low"
    assert "[example.com]" in out["answer"] and "[docs.other.org]" in out["answer"]


def test_max_results_is_clamped(capture_post) -> None:
    calls = capture_post({"answer": "x", "results": []})
    answer_from_web(question="q", max_results=50)
    answer_from_web(question="q", max_results=0)
    assert [c["json"]["max_results"] for c in calls] == [10, 5]


def test_empty_question_returns_error_without_calling_api(capture_post) -> None:
    calls = capture_post({"answer": "x", "results": []})
    out = answer_from_web(question="   ")
    assert out["error"] == "ValueError"
    assert calls == []


def test_missing_api_key_returns_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("TAVILY_API_KEY", raising=False)
    out = answer_from_web(question="RAG là gì?")
    assert out["tool"] == "answer_from_web" and out["error"] == "RuntimeError"
