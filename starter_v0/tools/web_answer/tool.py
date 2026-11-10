from __future__ import annotations

import os
import re
from typing import Any

import requests

from tools._shared import TIMEOUT, domain, err

MAX_SNIPPET_CHARS = 600


def _first_sentences(text: str, limit: int = 2) -> str:
    sentences = re.split(r"(?<=[.!?])\s+", (text or "").strip())
    return " ".join(s for s in sentences[:limit] if s).strip()


def _fallback_answer(items: list[dict[str, Any]]) -> str:
    """Build a short evidence-based answer from the top snippets when Tavily returns no answer."""
    parts = []
    for item in items[:3]:
        snippet = _first_sentences(item.get("summary") or "")
        if snippet:
            parts.append(f"{snippet} [{item.get('source') or item.get('url')}]")
    return " ".join(parts)


def answer_from_web(question: str = "", max_results: int = 5) -> dict[str, Any]:
    """Fallback research tool: search the web for a free-form question and synthesize an answer with sources.

    Used when no specialised tool fits (not news-by-timeframe, not tweets, not a given URL, not arXiv, not policy).
    Returns `answer` (synthesized by Tavily, or stitched from the top snippets) plus the `items` it is based on.
    """
    try:
        question = (question or "").strip()
        if not question:
            raise ValueError("Empty question")
        key = os.getenv("TAVILY_API_KEY")
        if not key:
            raise RuntimeError("Missing TAVILY_API_KEY env var")
        limit = max(1, min(int(max_results or 5), 10))
        response = requests.post(
            "https://api.tavily.com/search",
            json={
                "query": question,
                "topic": "general",
                "search_depth": "advanced",
                "include_answer": "advanced",
                "max_results": limit,
            },
            headers={"Authorization": f"Bearer {key}"},
            timeout=TIMEOUT,
        )
        response.raise_for_status()
        data = response.json()
        items = [{
            "title": item.get("title"),
            "url": item.get("url"),
            "source": domain(item.get("url", "")),
            "summary": (item.get("content") or "")[:MAX_SNIPPET_CHARS],
            "score": item.get("score"),
        } for item in data.get("results", [])]

        answer = (data.get("answer") or "").strip()
        answer_source = "tavily_answer"
        if not answer:
            answer = _fallback_answer(items)
            answer_source = "top_snippets" if answer else "none"

        return {
            "tool": "answer_from_web",
            "question": question,
            "answer": answer,
            "answer_source": answer_source,
            "confidence": "low" if answer_source != "tavily_answer" or len(items) < 2 else "medium",
            "note": "Câu trả lời tổng hợp tự động từ web; cần trích nguồn khi trả lời người dùng và nói rõ nếu nguồn không thống nhất.",
            "items": items,
        }
    except Exception as exc:
        return err("answer_from_web", exc)
