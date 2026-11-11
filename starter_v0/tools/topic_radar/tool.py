"""Compare small samples of Tavily news and RapidAPI Twitter/X search results."""
from __future__ import annotations

import os
import ipaddress
import re
from typing import Any
from urllib.parse import urlsplit

import requests

from tools._shared import TIMEOUT, domain, err, terms

NAME = "topic_radar"


def _request_news(query: str, timeframe: str, limit: int) -> list[dict[str, Any]]:
    key = os.getenv("TAVILY_API_KEY")
    if not key:
        raise RuntimeError("Missing TAVILY_API_KEY")
    response = requests.post(
        "https://api.tavily.com/search",
        json={"query": query, "topic": "news", "time_range": timeframe,
              "max_results": limit, "search_depth": "basic"},
        headers={"Authorization": f"Bearer {key}"}, timeout=TIMEOUT,
    )
    response.raise_for_status()
    data = response.json()
    if not isinstance(data, dict):
        raise ValueError("Invalid Tavily response")
    return data.get("results") or []


def _request_social(query: str) -> list[dict[str, Any]]:
    key = os.getenv("RAPIDAPI_KEY")
    host = os.getenv("RAPIDAPI_TWITTER_HOST", "twitter-api45.p.rapidapi.com")
    if not key:
        raise RuntimeError("Missing RAPIDAPI_KEY")
    if not re.fullmatch(r"[a-z0-9-]+\.p\.rapidapi\.com", host):
        raise ValueError("Invalid RAPIDAPI_TWITTER_HOST")
    response = requests.get(
        f"https://{host}/search.php", params={"query": query, "search_type": "Latest"},
        headers={"x-rapidapi-key": key, "x-rapidapi-host": host}, timeout=TIMEOUT,
    )
    response.raise_for_status()
    data = response.json()
    if not isinstance(data, dict):
        raise ValueError("Invalid RapidAPI response")
    return data.get("timeline") or data.get("tweets") or []


def _valid_public_url(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    try:
        parsed = urlsplit(value)
        host = (parsed.hostname or "").lower()
        if (parsed.scheme not in ("http", "https") or parsed.username or not host
                or host in {"localhost", "localhost.localdomain"}
                or host.endswith((".local", ".internal"))
                or not re.fullmatch(r"[a-z0-9.-]+", host)):
            return False
        try:
            return ipaddress.ip_address(host).is_global
        except ValueError:
            return "." in host and ".." not in host
    except ValueError:
        return False


def _enrich(url: str) -> tuple[str, str]:
    """Best-effort article scrape, with Tavily extract as backup."""
    key = os.getenv("FIRECRAWL_API_KEY")
    if key:
        try:
            response = requests.post(
                "https://api.firecrawl.dev/v2/scrape",
                json={"url": url, "formats": ["markdown"], "onlyMainContent": True},
                headers={"Authorization": f"Bearer {key}"}, timeout=TIMEOUT,
            )
            response.raise_for_status()
            data = response.json()
            content = (data.get("data") or {}).get("markdown") or "" if data.get("success") is not False else ""
            if content.strip():
                return content[:1200], "firecrawl"
        except (requests.RequestException, ValueError, TypeError, AttributeError):
            pass
    key = os.getenv("TAVILY_API_KEY")
    if key:
        try:
            response = requests.post(
                "https://api.tavily.com/extract", json={"urls": [url], "extract_depth": "basic"},
                headers={"Authorization": f"Bearer {key}"}, timeout=TIMEOUT,
            )
            response.raise_for_status()
            results = response.json().get("results") or []
            content = (results[0].get("raw_content") or "") if results else ""
            if content.strip():
                return content[:1200], "tavily_extract"
        except (requests.RequestException, ValueError, TypeError, AttributeError):
            pass
    return "", "search_snippet"


def compare_topic_signals(query: str = "", timeframe: str = "week", limit: int = 5,
                          include_social: bool = True, enrich_articles: bool = False) -> dict[str, Any]:
    """Return cited samples and overlap, NOT a population-level trending score."""
    try:
        if not isinstance(query, str) or not 2 <= len(query.strip()) <= 250:
            raise ValueError("query must have 2–250 characters")
        if timeframe not in {"day", "week", "month", "year"}:
            raise ValueError("timeframe must be day, week, month or year")
        if type(limit) is not int or not 1 <= limit <= 10:
            raise ValueError("limit must be an integer from 1 to 10")
        if type(include_social) is not bool or type(enrich_articles) is not bool:
            raise ValueError("include_social and enrich_articles must be boolean")
        warnings: list[str] = []
        news: list[dict[str, Any]] = []
        posts: list[dict[str, Any]] = []
        ok_providers = 0
        try:
            seen_urls: set[str] = set()
            for raw in _request_news(query.strip(), timeframe, limit):
                if not isinstance(raw, dict) or not _valid_public_url(raw.get("url")):
                    continue
                url = raw["url"].split("#", 1)[0]
                if url in seen_urls:
                    continue
                seen_urls.add(url)
                news.append({
                    "title": raw.get("title") or url, "url": url,
                    "source": domain(url), "summary": str(raw.get("content") or "")[:1200],
                    "date": raw.get("published_date"), "section": "news", "provider": "tavily",
                })
                if len(news) == limit:
                    break
            ok_providers += 1
        except (requests.RequestException, ValueError, TypeError, RuntimeError) as exc:
            warnings.append(f"Tavily news unavailable: {type(exc).__name__}")

        if enrich_articles:
            for item in news[:2]:  # At most two extra URLs / two providers per URL
                summary, provider = _enrich(item["url"])
                if summary:
                    item["summary"] = summary
                    item["provider"] = provider
                else:
                    warnings.append("Article extraction failed; kept search snippet")

        if include_social:
            try:
                seen_ids: set[str] = set()
                for raw in _request_social(query.strip()):
                    if not isinstance(raw, dict):
                        continue
                    tid = str(raw.get("tweet_id") or raw.get("id") or "").strip()
                    if not tid.isdigit() or tid in seen_ids:
                        continue
                    seen_ids.add(tid)
                    author = raw.get("author") if isinstance(raw.get("author"), dict) else {}
                    handle = raw.get("screen_name") or author.get("screen_name") or ""
                    handle = handle if re.fullmatch(r"[a-zA-Z0-9_]{1,15}", handle) else "i"
                    body = str(raw.get("text") or "")
                    posts.append({
                        "title": body[:110], "summary": body[:900],
                        "url": f"https://x.com/{handle}/status/{tid}" if handle != "i"
                               else f"https://x.com/i/status/{tid}",
                        "source": "x.com", "section": "social", "provider": "rapidapi",
                        "date": raw.get("created_at"),
                        "metrics": {"likes": raw.get("favorites"), "retweets": raw.get("retweets")},
                    })
                    if len(posts) >= limit:
                        break
                ok_providers += 1
            except (requests.RequestException, ValueError, TypeError, RuntimeError) as exc:
                warnings.append(f"RapidAPI X unavailable: {type(exc).__name__}")

        if not ok_providers:
            raise RuntimeError("Neither Tavily nor RapidAPI returned a usable API response")
        web_terms = set().union(*(terms(i["title"] + " " + i["summary"]) for i in news))
        social_terms = set().union(*(terms(i["summary"]) for i in posts))
        return {
            "tool": NAME, "query": query.strip(), "timeframe": timeframe,
            "items": news + posts,
            "signals": {
                "news_results": len(news),
                "news_domains": len({domain(i["url"]) for i in news}),
                "x_post_results": len(posts),
                "shared_terms": sorted(web_terms & social_terms)[:15],
            },
            "status": "partial" if warnings else "ok", "warnings": warnings,
            "note": "These are small API samples; counts and overlap are not proof of popularity or truth.",
        }
    except Exception as exc:
        return err(NAME, exc)
