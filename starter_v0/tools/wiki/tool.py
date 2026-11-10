from __future__ import annotations

from typing import Any

import requests

from tools._shared import TIMEOUT, err


SUPPORTED_LANGS = {"en", "vi"}
DEFAULT_LANG = "en"
MAX_RESULTS_CAP = 5
SUMMARY_SENTENCES = 4
# Wikimedia yêu cầu User-Agent mô tả client; không dùng thông tin cá nhân.
USER_AGENT = "AI20k-Day03-Research-Agent/1.0 (educational lab)"


def _api_url(lang: str) -> str:
    return f"https://{lang}.wikipedia.org/w/api.php"


def _clamp_max_results(value: Any) -> int:
    """Model có thể gửi '5', 0, -1, None hoặc 100 — đưa về khoảng [1, MAX_RESULTS_CAP]."""
    try:
        number = int(value)
    except (TypeError, ValueError):
        number = 3
    return max(1, min(number, MAX_RESULTS_CAP))


def wiki_search(query: str = "", lang: str = DEFAULT_LANG, max_results: int = 3) -> dict[str, Any]:
    """Tìm bài Wikipedia theo từ khóa, trả về đoạn mở đầu (plain text) của từng bài.

    Một request duy nhất tới MediaWiki Action API: generator=search + prop=extracts|info.
    Item trả về có title/url/source/summary để đưa thẳng vào tool `format`.
    """
    try:
        cleaned = " ".join(str(query or "").split())
        if not cleaned:
            raise ValueError("query is empty: pass the topic to look up on Wikipedia")
        lang = (lang or "").strip().lower()
        lang = lang if lang in SUPPORTED_LANGS else DEFAULT_LANG
        max_results = _clamp_max_results(max_results)

        params = {
            "action": "query",
            "format": "json",
            "formatversion": 2,
            "generator": "search",
            "gsrsearch": cleaned,
            "gsrlimit": max_results,
            "prop": "extracts|info",
            "exintro": 1,
            "explaintext": 1,
            "exsentences": SUMMARY_SENTENCES,
            "inprop": "url",
            "redirects": 1,
        }
        response = requests.get(_api_url(lang), params=params, headers={"User-Agent": USER_AGENT}, timeout=TIMEOUT)
        response.raise_for_status()
        data = response.json()
        if "error" in data:
            raise RuntimeError(f"Wikipedia API error: {data['error'].get('info', data['error'])}")

        pages = (data.get("query") or {}).get("pages") or []
        if isinstance(pages, dict):  # formatversion=1 trả dict theo pageid
            pages = list(pages.values())
        pages = [page for page in pages if not page.get("missing") and page.get("title")]
        pages.sort(key=lambda page: page.get("index", 0))

        items = [{
            "title": page["title"],
            "url": page.get("fullurl") or f"https://{lang}.wikipedia.org/wiki/{page['title'].replace(' ', '_')}",
            "source": f"{lang}.wikipedia.org",
            "summary": " ".join((page.get("extract") or "").split()),
            "pageid": page.get("pageid"),
        } for page in pages[:max_results]]

        return {"tool": "wiki_search", "query": cleaned, "lang": lang, "items": items, "item_count": len(items)}
    except Exception as exc:
        return err("wiki_search", exc)
