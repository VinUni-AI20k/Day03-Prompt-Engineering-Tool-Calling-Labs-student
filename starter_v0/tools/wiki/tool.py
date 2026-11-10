from __future__ import annotations

import re
from typing import Any
from urllib.parse import quote

import requests

from tools._shared import TIMEOUT, err

HEADERS = {"User-Agent": "ResearchAgentToolEval/1.0 (student lab)", "Accept": "application/json"}


def wiki_summary(title: str = "", lang: str = "vi") -> dict[str, Any]:
    try:
        title = str(title or "").strip()
        if not title:
            raise ValueError("title must be a non-empty string")
        lang = str(lang or "vi").strip().lower()
        # lang goes into the hostname: only allow plain language codes.
        if not re.fullmatch(r"[a-z]{2,3}", lang):
            raise ValueError(f"invalid lang code: {lang!r}")
        response = requests.get(
            f"https://{lang}.wikipedia.org/api/rest_v1/page/summary/{quote(title.replace(' ', '_'), safe='')}",
            headers=HEADERS,
            timeout=TIMEOUT,
        )
        if response.status_code == 404:
            return {"tool": "wiki_summary", "title": title, "lang": lang, "found": False}
        response.raise_for_status()
        data = response.json()
        return {
            "tool": "wiki_summary",
            "title": data.get("title", title),
            "lang": lang,
            "found": True,
            "is_disambiguation": data.get("type") == "disambiguation",
            "description": data.get("description"),
            "summary": data.get("extract"),
            "url": (data.get("content_urls") or {}).get("desktop", {}).get("page"),
        }
    except Exception as exc:
        return err("wiki_summary", exc)
