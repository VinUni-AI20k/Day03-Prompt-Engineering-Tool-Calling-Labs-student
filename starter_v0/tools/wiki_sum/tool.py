from __future__ import annotations

from typing import Any
from urllib.parse import quote

import requests

from tools._shared import TIMEOUT, err


WIKIPEDIA_SUMMARY_URL = "https://en.wikipedia.org/api/rest_v1/page/summary/"


def wiki_sum(title: str = "") -> dict[str, Any]:
    try:
        if not isinstance(title, str) or not title.strip():
            raise ValueError("title must be a non-empty Wikipedia page title")

        page_title = title.strip().replace(" ", "_")
        response = requests.get(
            WIKIPEDIA_SUMMARY_URL + quote(page_title, safe="()"),
            headers={"Accept": "application/json"},
            timeout=TIMEOUT,
        )
        response.raise_for_status()
        data = response.json()
        extract = data.get("extract")
        if not isinstance(extract, str) or not extract.strip():
            raise ValueError("Wikipedia response did not contain a summary")

        return {
            "tool": "wiki_sum",
            "title": data.get("title", title.strip()),
            "summary": extract,
            "url": data.get("content_urls", {}).get("desktop", {}).get("page"),
            "description": data.get("description"),
        }
    except Exception as exc:
        return err("wiki_sum", exc)
