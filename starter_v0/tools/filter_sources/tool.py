from __future__ import annotations

import math
from typing import Any
from urllib.parse import urlsplit

from tools._shared import err


def _domain(url: Any) -> str:
    if not isinstance(url, str):
        return ""
    try:
        parts = urlsplit(url)
        if parts.scheme not in {"http", "https"} or not parts.hostname:
            return ""
        return parts.hostname.lower().removeprefix("www.").rstrip(".")
    except ValueError:
        return ""


def filter_sources(
    items: list[dict[str, Any]] | None = None,
    domains: list[str] | None = None,
    min_score: float | None = None,
) -> dict[str, Any]:
    """Filter collected sources by publisher domain and/or minimum score."""
    try:
        if not isinstance(items, list):
            raise TypeError("items must be a list of research item objects")
        wanted_domains: set[str] | None = None
        if domains is not None:
            if not isinstance(domains, list) or any(not isinstance(d, str) or not d.strip() for d in domains):
                raise TypeError("domains must be a list of non-empty domain strings")
            wanted_domains = {d.lower().strip().removeprefix("www.").rstrip(".") for d in domains}
        if min_score is not None:
            if isinstance(min_score, bool) or not isinstance(min_score, (int, float)) or not math.isfinite(min_score):
                raise ValueError("min_score must be a finite number or null")

        matched: list[dict[str, Any]] = []
        for index, item in enumerate(items):
            if not isinstance(item, dict):
                raise TypeError(f"items[{index}] must be an object")
            if wanted_domains is not None and _domain(item.get("url")) not in wanted_domains:
                continue
            if min_score is not None:
                score = item.get("score")
                if isinstance(score, bool) or not isinstance(score, (int, float)) or not math.isfinite(score):
                    raise ValueError(f"items[{index}].score must be a finite number when min_score is set")
                if score < min_score:
                    continue
            matched.append(item)

        return {
            "tool": "filter_sources",
            "items": matched,
            "item_count": len(matched),
            "domains": sorted(wanted_domains) if wanted_domains is not None else None,
            "min_score": min_score,
        }
    except Exception as exc:
        return err("filter_sources", exc)
