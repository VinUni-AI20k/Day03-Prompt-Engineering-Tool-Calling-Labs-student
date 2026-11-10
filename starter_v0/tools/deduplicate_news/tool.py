from __future__ import annotations

from typing import Any
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from tools._shared import err, terms


_TRACKING_PARAMS = {"fbclid", "gclid", "mc_cid", "mc_eid"}


def _normalize_url(url: str) -> str:
    value = url.strip()
    if not value:
        return ""
    if "://" not in value:
        value = f"https://{value}"

    try:
        parsed = urlsplit(value)
        scheme = parsed.scheme.lower()
        host = parsed.hostname
        port = parsed.port
    except ValueError:
        return ""

    if scheme not in {"http", "https"} or not host or parsed.username or parsed.password:
        return ""

    host = host.lower().rstrip(".")
    if host.startswith("www."):
        host = host[4:]
    if ":" in host and not host.startswith("["):
        host = f"[{host}]"

    netloc = host
    if port is not None and not (scheme == "http" and port == 80) and not (scheme == "https" and port == 443):
        netloc = f"{netloc}:{port}"

    path = parsed.path or "/"
    if path != "/":
        path = path.rstrip("/") or "/"

    query = sorted(
        (key, value)
        for key, value in parse_qsl(parsed.query, keep_blank_values=True)
        if not key.lower().startswith("utm_") and key.lower() not in _TRACKING_PARAMS
    )
    return urlunsplit((scheme, netloc, path, urlencode(query), ""))


def _title_similarity(left: set[str], right: set[str]) -> float:
    if not left or not right:
        return 0.0
    return len(left & right) / max(len(left), len(right))


def deduplicate_news(
    items: list[dict[str, Any]] | None = None,
    title_similarity_threshold: float = 0.8,
) -> dict[str, Any]:
    """Merge duplicate news by normalized URL, then by shared title terms."""
    if not isinstance(items, list):
        return err("deduplicate_news", ValueError("items must be a list"))
    if (
        isinstance(title_similarity_threshold, bool)
        or not isinstance(title_similarity_threshold, (int, float))
        or not 0 < title_similarity_threshold <= 1
    ):
        return err("deduplicate_news", ValueError("title_similarity_threshold must be greater than 0 and at most 1"))

    groups: list[dict[str, Any]] = []
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            return err("deduplicate_news", ValueError(f"items[{index}] must be an object"))
        title = item.get("title")
        if not isinstance(title, str) or not title.strip():
            return err("deduplicate_news", ValueError(f"items[{index}].title must be a non-empty string"))
        for field in ("url", "source", "summary", "section"):
            if item.get(field) is not None and not isinstance(item[field], str):
                return err("deduplicate_news", ValueError(f"items[{index}].{field} must be a string"))

        normalized_url = _normalize_url(item.get("url") or "")
        title_terms = terms(title)
        matching_group: dict[str, Any] | None = None

        if normalized_url:
            matching_group = next(
                (group for group in groups if normalized_url in group["urls"]),
                None,
            )

        if matching_group is None:
            best_similarity = 0.0
            for group in groups:
                similarity = max(
                    (_title_similarity(title_terms, existing) for existing in group["titles"]),
                    default=0.0,
                )
                if similarity >= title_similarity_threshold and similarity > best_similarity:
                    matching_group = group
                    best_similarity = similarity

        if matching_group is None:
            record = dict(item)
            source = (item.get("source") or "").strip()
            groups.append({
                "item": record,
                "urls": {normalized_url} if normalized_url else set(),
                "titles": [title_terms],
                "sources": [source] if source else [],
            })
            continue

        matching_group["titles"].append(title_terms)
        if normalized_url:
            matching_group["urls"].add(normalized_url)

        source = (item.get("source") or "").strip()
        if source and source not in matching_group["sources"]:
            matching_group["sources"].append(source)
        if matching_group["sources"]:
            matching_group["item"]["source"] = ", ".join(matching_group["sources"])

        summary = item.get("summary") or ""
        if len(summary) > len(matching_group["item"].get("summary") or ""):
            matching_group["item"]["summary"] = summary

    merged_items = [group["item"] for group in groups]
    return {
        "tool": "deduplicate_news",
        "items": merged_items,
        "item_count": len(merged_items),
        "duplicates_removed": len(items) - len(merged_items),
    }
