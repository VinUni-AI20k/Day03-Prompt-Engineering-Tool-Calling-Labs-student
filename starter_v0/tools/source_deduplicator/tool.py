"""Remove duplicate research results; optionally compare extracted page content."""
from __future__ import annotations

import os
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlsplit

import requests
from tools._shared import TIMEOUT, err, terms

TRACKERS = {"fbclid", "gclid", "mc_cid", "mc_eid", "ref_src"}


def _url_key(url: str) -> str:
    if not isinstance(url, str):
        raise ValueError("Each item needs an HTTP(S) url")
    parsed = urlsplit(url.strip())
    if parsed.scheme not in ("http", "https") or not parsed.hostname or parsed.username:
        raise ValueError("Each item needs an HTTP(S) url")
    host = parsed.hostname.lower().removeprefix("www.")
    if host == "localhost" or host.endswith(".local"):
        raise ValueError("Local URLs are not allowed")
    query = sorted((k, v) for k, v in parse_qsl(parsed.query)
                   if not k.lower().startswith("utm_") and k.lower() not in TRACKERS)
    return f"{host}{parsed.path.rstrip('/') or '/'}?{urlencode(query)}"


def _similar(a: set[str], b: set[str], threshold: float) -> bool:
    return bool(a and b and len(a & b) / len(a | b) >= threshold)


def _read_content(url: str) -> str:
    """Use Firecrawl first; fall back to Tavily Extract if Firecrawl fails."""
    providers = (
        ("FIRECRAWL_API_KEY", "https://api.firecrawl.dev/v2/scrape",
         {"url": url, "formats": ["markdown"], "onlyMainContent": True}),
        ("TAVILY_API_KEY", "https://api.tavily.com/extract",
         {"urls": [url], "extract_depth": "basic"}),
    )
    errors = []
    for env, endpoint, body in providers:
        key = os.getenv(env)
        if not key:
            continue
        try:
            response = requests.post(endpoint, json=body,
                                     headers={"Authorization": f"Bearer {key}"}, timeout=TIMEOUT)
            response.raise_for_status()
            payload = response.json()
            if env == "FIRECRAWL_API_KEY":
                content = (payload.get("data") or {}).get("markdown") or ""
            else:
                results = payload.get("results") or []
                content = results[0].get("raw_content") or "" if results else ""
            if len(content.strip()) >= 50:
                return content[:15000]
            errors.append(f"{env}: empty or short content")
        except (requests.RequestException, ValueError, TypeError, KeyError) as exc:
            errors.append(f"{env}: {type(exc).__name__}")
    raise RuntimeError("Extraction failed: " + ("; ".join(errors) or "no Firecrawl/Tavily API key"))


def deduplicate_sources(items: list[dict[str, Any]] | None = None,
                        verify_content: bool = False) -> dict[str, Any]:
    """Return original items in original order, without duplicate sources."""
    name = "source_deduplicator"
    try:
        if not isinstance(items, list) or any(not isinstance(x, dict) for x in items):
            raise ValueError("items must be a list of objects")
        if not isinstance(verify_content, bool):
            raise ValueError("verify_content must be boolean")
        if verify_content and len(items) > 8:
            raise ValueError("verify_content supports at most 8 items per call")
        if verify_content and not (os.getenv("FIRECRAWL_API_KEY") or os.getenv("TAVILY_API_KEY")):
            raise RuntimeError("Missing FIRECRAWL_API_KEY or TAVILY_API_KEY")
        unique, keys, titles, bodies = [], [], [], []
        for item in items:
            url = item.get("url", "")
            key = _url_key(url)
            title = terms(item.get("title") or "")
            if key in keys:
                continue
            body = terms(_read_content(url)) if verify_content else set()
            duplicate = any(
                _similar(body, old_body, 0.80) if verify_content
                else len(title) >= 4 and _similar(title, old_title, 0.90)
                for old_title, old_body in zip(titles, bodies)
            )
            if not duplicate:
                unique.append(item)
                keys.append(key)
                titles.append(title)
                bodies.append(body)
        return {"tool": name, "items": unique, "removed": len(items) - len(unique),
                "checked": len(items), "verification": "content" if verify_content else "local"}
    except Exception as exc:
        return err(name, exc)
