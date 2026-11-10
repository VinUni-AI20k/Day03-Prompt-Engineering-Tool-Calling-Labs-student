from __future__ import annotations

from typing import Any

import requests

from tools._limits import pick
from tools._shared import TIMEOUT, err

USER_AGENT = "AI20k-Day03-Research-Agent/1.0 (educational lab)"


def wikipedia_summary(query: str = "", lang: str = "en") -> dict[str, Any]:
    """Find the best-matching Wikipedia article and return its intro paragraph (no key)."""
    try:
        query = (query or "").strip()
        if not query:
            raise ValueError("query must not be empty")
        lang = pick(lang, ("en", "vi"), "en")
        response = requests.get(
            f"https://{lang}.wikipedia.org/w/api.php",
            params={
                "action": "query", "format": "json", "formatversion": 2,
                "generator": "search", "gsrsearch": query, "gsrlimit": 1,
                "prop": "extracts|info", "exintro": 1, "explaintext": 1, "inprop": "url",
            },
            headers={"User-Agent": USER_AGENT},
            timeout=TIMEOUT,
        )
        response.raise_for_status()
        pages = (response.json().get("query") or {}).get("pages") or []
        items = []
        for page in pages[:1]:
            extract = (page.get("extract") or "").strip()
            items.append({
                "title": page.get("title") or "",
                "url": page.get("fullurl") or "",
                "source": f"{lang}.wikipedia.org",
                "summary": extract[:1500] + ("..." if len(extract) > 1500 else ""),
            })
        return {"tool": "wikipedia_summary", "query": query, "lang": lang, "items": items}
    except Exception as exc:
        return err("wikipedia_summary", exc)
