"""Fetch and parse RSS or Atom XML feeds into structured research items."""
from __future__ import annotations

import html
import ipaddress
import re
import xml.etree.ElementTree as ET
from typing import Any
from urllib.parse import urljoin, urlsplit

import requests

from tools._shared import TIMEOUT, domain, err, fold_text

NAME = "rss_feed_reader"
USER_AGENT = "AI20k-Day03-Research-Agent/1.0 (rss_feed_reader)"
MAX_FEED_CHARS = 2_000_000


def _validate_feed_url(value: Any) -> str:
    """Ensure URL is a well-formed public HTTP(S) URL."""
    if not isinstance(value, str) or not value.strip():
        raise ValueError("url must be a non-empty HTTP(S) URL")
    cleaned = value.strip()
    parsed = urlsplit(cleaned)
    host = (parsed.hostname or "").lower()
    if parsed.scheme not in {"http", "https"} or not host or parsed.username or parsed.password:
        raise ValueError("url must be a valid HTTP(S) URL without credentials")
    if host in {"localhost", "localhost.localdomain"} or host.endswith((".local", ".internal", ".localhost")):
        raise ValueError("Local or internal URLs are not allowed")
    try:
        if not ipaddress.ip_address(host).is_global:
            raise ValueError("Private or non-global IP URLs are not allowed")
    except ValueError as exc:
        if "not allowed" in str(exc):
            raise
        if "." not in host or ".." in host or not re.fullmatch(r"[a-z0-9.-]+", host):
            raise ValueError("url hostname is invalid")
    return cleaned


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1].lower() if isinstance(tag, str) else ""


def _child_text(parent: ET.Element, names: tuple[str, ...]) -> str:
    wanted = {n.lower() for n in names}
    for child in parent:
        if _local_name(child.tag) in wanted:
            text = "".join(child.itertext()).strip()
            if text:
                return text
    return ""


def _clean_text(value: str, max_len: int = 400) -> str:
    if not value:
        return ""
    unescaped = html.unescape(value)
    stripped = re.sub(r"<[^>]+>", " ", unescaped)
    normalized = " ".join(html.unescape(stripped).split())
    if len(normalized) <= max_len:
        return normalized
    return normalized[: max_len - 3].rstrip() + "..."


def _extract_entry_url(entry: ET.Element, feed_url: str, is_atom: bool) -> str:
    if is_atom:
        fallback_href = ""
        for child in entry:
            if _local_name(child.tag) != "link":
                continue
            href = (child.attrib.get("href") or "").strip() or (child.text or "").strip()
            if not href:
                continue
            rel = (child.attrib.get("rel") or "alternate").lower()
            if rel == "alternate":
                return urljoin(feed_url, href)
            if not fallback_href:
                fallback_href = href
        if fallback_href:
            return urljoin(feed_url, fallback_href)
        candidate_id = _child_text(entry, ("id",))
        return candidate_id if candidate_id.startswith(("http://", "https://")) else ""

    link = _child_text(entry, ("link",))
    if link:
        return urljoin(feed_url, link)
    guid = _child_text(entry, ("guid",))
    return guid if guid.startswith(("http://", "https://")) else ""


def _parse_feed_xml(raw_xml: str, feed_url: str) -> tuple[str, str, list[dict[str, str]]]:
    if not raw_xml or not raw_xml.strip():
        raise ValueError("Feed response is empty")
    if len(raw_xml) > MAX_FEED_CHARS:
        raise ValueError("Feed response exceeds maximum supported size")
    if re.search(r"<!(?:DOCTYPE|ENTITY)\b", raw_xml[:4096], re.IGNORECASE):
        raise ValueError("XML DOCTYPE/ENTITY declarations are not allowed")

    root = ET.fromstring(raw_xml.lstrip("\ufeff\r\n\t "))
    root_name = _local_name(root.tag)

    if root_name == "feed":
        feed_type = "atom"
        feed_title = _clean_text(_child_text(root, ("title",)), max_len=200)
        entries = [child for child in root if _local_name(child.tag) == "entry"]
    elif root_name in {"rss", "rdf"}:
        feed_type = "rss"
        channel = next((child for child in root if _local_name(child.tag) == "channel"), None)
        if channel is None:
            raise ValueError("Invalid RSS feed: missing <channel> element")
        feed_title = _clean_text(_child_text(channel, ("title",)), max_len=200)
        entries = [child for child in channel if _local_name(child.tag) == "item"]
        if not entries and root_name == "rdf":
            entries = [child for child in root if _local_name(child.tag) == "item"]
    else:
        raise ValueError(f"URL did not return a valid RSS or Atom feed (root element: '{root_name}')")

    parsed_items: list[dict[str, str]] = []
    is_atom = feed_type == "atom"
    for entry in entries:
        title = _clean_text(_child_text(entry, ("title",)), max_len=240)
        entry_url = _extract_entry_url(entry, feed_url, is_atom=is_atom)
        if not title and not entry_url:
            continue
        published = _clean_text(_child_text(entry, ("pubdate", "published", "updated", "date")), max_len=64)
        summary = _clean_text(_child_text(entry, ("description", "summary", "encoded", "content")), max_len=400)
        parsed_items.append({
            "title": title or entry_url,
            "url": entry_url or feed_url,
            "source": domain(entry_url or feed_url) or domain(feed_url),
            "published": published,
            "summary": summary,
        })
    return feed_type, feed_title, parsed_items


def read_rss_feed(url: str = "", max_items: int = 5, keyword: str = "") -> dict[str, Any]:
    """Fetch an RSS or Atom feed URL and return normalized recent items."""
    try:
        feed_url = _validate_feed_url(url)
        if isinstance(max_items, bool) or not isinstance(max_items, int) or not (1 <= max_items <= 20):
            raise ValueError("max_items must be an integer between 1 and 20")
        if not isinstance(keyword, str):
            raise ValueError("keyword must be a string")

        response = requests.get(
            feed_url,
            headers={
                "User-Agent": USER_AGENT,
                "Accept": "application/rss+xml, application/atom+xml, application/xml, text/xml;q=0.9",
            },
            timeout=TIMEOUT,
        )
        final_url = getattr(response, "url", None)
        if isinstance(final_url, str) and final_url:
            _validate_feed_url(final_url)
        response.raise_for_status()

        raw_xml = response.text or (response.content.decode("utf-8", errors="replace") if response.content else "")
        feed_type, feed_title, all_items = _parse_feed_xml(raw_xml, final_url or feed_url)

        needle = fold_text(keyword.strip()) if keyword.strip() else ""
        if needle:
            filtered = [
                item for item in all_items
                if needle in fold_text(f"{item['title']} {item['summary']}")
            ]
        else:
            filtered = all_items

        items = filtered[:max_items]
        return {
            "tool": NAME,
            "status": "ok",
            "feed_url": feed_url,
            "feed_title": feed_title,
            "feed_type": feed_type,
            "count": len(items),
            "items": items,
        }
    except Exception as exc:
        return err(NAME, exc)

