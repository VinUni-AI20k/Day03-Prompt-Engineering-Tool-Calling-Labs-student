from __future__ import annotations

import os
from typing import Any

import requests

from tools._shared import TIMEOUT, domain, err


def get_weather(location: str = "", timeframe: str = "today") -> dict[str, Any]:
    try:
        if not location or not location.strip():
            raise ValueError("Location cannot be empty")

        key = os.getenv("TAVILY_API_KEY")
        if not key:
            raise RuntimeError("Missing TAVILY_API_KEY env var")

        query = f"weather forecast {location.strip()} {timeframe}".strip()
        body: dict[str, Any] = {
            "query": query,
            "search_depth": "basic",
            "max_results": 3,
            "include_answer": True,
        }

        response = requests.post(
            "https://api.tavily.com/search",
            json=body,
            headers={"Authorization": f"Bearer {key}"},
            timeout=TIMEOUT,
        )
        response.raise_for_status()
        data = response.json()

        items = [{
            "title": item.get("title"),
            "url": item.get("url"),
            "source": domain(item.get("url", "")),
            "snippet": item.get("content"),
        } for item in data.get("results", [])]

        summary = data.get("answer") or (items[0]["snippet"] if items else "No weather data found.")

        return {
            "tool": "weather",
            "location": location.strip(),
            "timeframe": timeframe,
            "summary": summary,
            "items": items,
        }
    except Exception as exc:
        return err("weather", exc)

