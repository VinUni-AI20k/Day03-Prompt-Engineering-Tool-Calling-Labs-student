from __future__ import annotations

from typing import Any
from urllib.parse import quote

import requests

from tools._shared import TIMEOUT, err

LANGS = {"en", "vi"}


def get_wikipedia_summary(title: str = "", lang: str = "en") -> dict[str, Any]:
    try:
        if not isinstance(title, str) or not title.strip():
            raise ValueError("title must be a non-empty string")
        if lang not in LANGS:
            raise ValueError(f"lang must be one of {sorted(LANGS)}")
        title = title.strip()

        response = requests.get(
            f"https://{lang}.wikipedia.org/api/rest_v1/page/summary/{quote(title.replace(' ', '_'), safe='')}",
            headers={"Accept": "application/json", "User-Agent": "Day03-Research-Agent"},
            timeout=TIMEOUT,
        )
        response.raise_for_status()
        data = response.json()
        if not isinstance(data, dict) or "title" not in data:
            raise ValueError("Wikipedia response has no title")

        page_url = ((data.get("content_urls") or {}).get("desktop") or {}).get("page") or ""
        return {
            "tool": "wikipedia",
            "items": [{
                "title": data["title"],
                "url": page_url,
                "source": f"{lang}.wikipedia.org",
                "summary": data.get("extract") or "",
                "description": data.get("description") or "",
                "is_disambiguation": data.get("type") == "disambiguation",
            }],
        }
    except Exception as exc:
        return err("wikipedia", exc)
