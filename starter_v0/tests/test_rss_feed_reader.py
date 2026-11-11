"""Unit tests for rss_feed_reader (100% offline with fake_http)."""
from __future__ import annotations

import pytest

from conftest import FakeResponse
from tools.rss_feed_reader.tool import read_rss_feed

SAMPLE_ATOM = """<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <title>arXiv cs.AI Updates</title>
  <entry>
    <title>Multi-Agent Tool Selection</title>
    <link rel="alternate" href="/abs/2611.00001" />
    <updated>2026-11-11T07:00:00Z</updated>
    <summary>Evaluates routing across multi-turn conversations.</summary>
  </entry>
  <entry>
    <title>Compiler Scheduling Study</title>
    <link rel="alternate" href="https://arxiv.org/abs/2611.00002" />
    <published>2026-11-10T12:00:00Z</published>
    <summary>Improves register allocation speed.</summary>
  </entry>
</feed>"""


def test_parses_atom_feed_and_resolves_relative_links(fake_http) -> None:
    fake_http(FakeResponse(text=SAMPLE_ATOM))
    result = read_rss_feed(url="https://arxiv.org/atom/cs.AI", max_items=5)

    assert result["status"] == "ok"
    assert result["feed_type"] == "atom"
    assert result["count"] == 2
    assert result["items"][0]["url"] == "https://arxiv.org/abs/2611.00001"
    assert result["items"][0]["published"] == "2026-11-11T07:00:00Z"


def test_keyword_filter_and_max_items_limit(fake_http) -> None:
    fake_http(FakeResponse(text=SAMPLE_ATOM))
    result = read_rss_feed(url="https://arxiv.org/atom/cs.AI", max_items=5, keyword="tool selection")

    assert result["count"] == 1
    assert result["items"][0]["title"] == "Multi-Agent Tool Selection"


def test_rejects_doctype_xml_expansion(fake_http) -> None:
    xml_with_doctype = """<?xml version="1.0"?>
    <!DOCTYPE rss [<!ENTITY xxe "boom">]>
    <rss version="2.0"><channel><title>X</title></channel></rss>"""
    fake_http(FakeResponse(text=xml_with_doctype))

    result = read_rss_feed(url="https://example.org/rss.xml")
    assert result["error"] == "ValueError"
    assert "DOCTYPE" in result["message"]


def test_rejects_private_ip_redirect_target(fake_http) -> None:
    resp = FakeResponse(text="<rss><channel><title>T</title></channel></rss>")
    resp.url = "http://169.254.169.254/latest/meta-data"
    fake_http(resp)

    result = read_rss_feed(url="https://example.org/rss.xml")
    assert result["error"] == "ValueError"


def test_network_exception_returns_error_dict(fake_http) -> None:
    fake_http(TimeoutError("connection timed out"))
    result = read_rss_feed(url="https://example.org/rss.xml")

    assert result["tool"] == "rss_feed_reader"
    assert result["error"] == "TimeoutError"
    assert "timed out" in result["message"]


@pytest.mark.parametrize("bad_url", ["", "ftp://example.org/feed.xml", "https://user:pass@example.org/rss.xml", "https://localhost.localdomain/feed"])
def test_rejects_invalid_or_unsafe_feed_urls(bad_url: str, fake_http) -> None:
    calls = fake_http(FakeResponse(text=""))
    result = read_rss_feed(url=bad_url)

    assert result["error"] == "ValueError"
    assert calls == []

