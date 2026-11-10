"""Find reviewable, source-linked evidence for a claim (not a truth verdict)."""
from __future__ import annotations

import ipaddress
import os
import re
from typing import Any
from urllib.parse import urlsplit

import requests

from tools._shared import TIMEOUT, domain, err, terms

NAME = "evidence_finder"


def _safe_url(value: Any) -> bool:
    """Reject malformed URLs and obvious internal / private destinations."""
    if not isinstance(value, str):
        return False
    try:
        parsed = urlsplit(value)
        host = (parsed.hostname or "").lower()
        if parsed.scheme not in {"http", "https"} or not host or parsed.username:
            return False
        if host in {"localhost", "localhost.localdomain"} or host.endswith((".local", ".internal")):
            return False
        if not re.fullmatch(r"[a-z0-9.-]+", host):
            return False
        try:
            return ipaddress.ip_address(host).is_global
        except ValueError:
            return "." in host and ".." not in host
    except ValueError:
        return False


def _post(url: str, key: str, body: dict[str, Any]) -> dict[str, Any]:
    response = requests.post(
        url, json=body, headers={"Authorization": f"Bearer {key}"}, timeout=TIMEOUT
    )
    response.raise_for_status()
    data = response.json()
    if not isinstance(data, dict) or data.get("success") is False:
        raise ValueError("Provider response is invalid or unsuccessful")
    return data


def _extract_page(url: str) -> tuple[str, str, list[str]]:
    """Firecrawl v2 first; Tavily Extract fallback. Limits extra paid calls."""
    warnings: list[str] = []
    fire_key = os.getenv("FIRECRAWL_API_KEY")
    tavily_key = os.getenv("TAVILY_API_KEY")
    if fire_key:
        try:
            data = _post("https://api.firecrawl.dev/v2/scrape", fire_key,
                         {"url": url, "formats": ["markdown"], "onlyMainContent": True})
            markdown = (data.get("data") or {}).get("markdown") or ""
            if isinstance(markdown, str) and len(markdown.strip()) >= 40:
                return markdown[:20000], "firecrawl", warnings
            warnings.append("Firecrawl returned too little content")
        except (requests.RequestException, ValueError, TypeError) as exc:
            warnings.append(f"Firecrawl: {type(exc).__name__}")
    if tavily_key:
        try:
            data = _post("https://api.tavily.com/extract", tavily_key,
                         {"urls": [url], "extract_depth": "basic"})
            results = data.get("results") or []
            content = (results[0].get("raw_content") or "") if results else ""
            if isinstance(content, str) and len(content.strip()) >= 40:
                return content[:20000], "tavily_extract", warnings
            warnings.append("Tavily Extract returned too little content")
        except (requests.RequestException, ValueError, TypeError, AttributeError) as exc:
            warnings.append(f"Tavily Extract: {type(exc).__name__}")
    return "", "search_snippet", warnings


def _best_excerpt(text: str, claim_tokens: set[str]) -> tuple[str, float]:
    """Rank passages by overlap; a relevance score is NOT evidence of truth."""
    passages = [p.strip() for p in re.split(r"\n+|(?<=[.!?])\s+", text) if p.strip()]
    if not passages:
        return "", 0.0
    best = max(passages, key=lambda p: len(terms(p) & claim_tokens))
    overlap = len(terms(best) & claim_tokens) / max(1, len(claim_tokens))
    return best[:420], round(overlap, 3)


def find_claim_evidence(claim: str = "", max_sources: int = 3,
                        deep_read: bool = True) -> dict[str, Any]:
    """Search different hostnames, optionally read pages, return traceable excerpts."""
    try:
        if not isinstance(claim, str) or not 5 <= len(claim.strip()) <= 350:
            raise ValueError("claim must have 5–350 characters")
        if type(max_sources) is not int or not 1 <= max_sources <= 5:
            raise ValueError("max_sources must be an integer from 1 to 5")
        if type(deep_read) is not bool:
            raise ValueError("deep_read must be boolean")
        key = os.getenv("TAVILY_API_KEY")
        if not key:
            raise RuntimeError("Missing TAVILY_API_KEY")
        search = _post("https://api.tavily.com/search", key, {
            "query": claim.strip(), "topic": "general", "search_depth": "basic",
            "max_results": min(20, max_sources * 3),
        })
        claim_tokens = terms(claim)
        used_domains: set[str] = set()
        items: list[dict[str, Any]] = []
        warnings: list[str] = []
        if deep_read and not (os.getenv("FIRECRAWL_API_KEY") or key):
            warnings.append("No extraction provider; using search snippets")
        for raw in search.get("results") or []:
            if not isinstance(raw, dict) or not _safe_url(raw.get("url")):
                continue
            url = raw["url"]
            host = domain(url).lower().removeprefix("www.")
            if host in used_domains:
                continue
            used_domains.add(host)
            provider = "search_snippet"
            text = str(raw.get("content") or raw.get("title") or "")
            if deep_read:
                extracted, provider, issues = _extract_page(url)
                text = extracted or text
                warnings.extend(issues)
            excerpt, relevance = _best_excerpt(text, claim_tokens)
            items.append({
                "title": raw.get("title") or url, "url": url, "source": host,
                "summary": excerpt, "relevance_score": relevance,
                "extraction_provider": provider,
            })
            if len(items) >= max_sources:
                break
        items.sort(key=lambda x: x["relevance_score"], reverse=True)
        return {
            "tool": NAME, "claim": claim.strip(), "items": items,
            "distinct_domains": len(items), "status": "ok" if items else "no_results",
            "warnings": sorted(set(warnings)),
            "assessment": "requires_review",
            "note": "Keyword overlap measures relevance, NOT whether the claim is true.",
        }
    except Exception as exc:
        return err(NAME, exc)
