"""Unit tests for the `dedupe` tool (offline, pure local)."""
from __future__ import annotations

from tools import TOOL_FUNCTIONS

dedupe = TOOL_FUNCTIONS["dedupe"]


def test_dedupe_by_url_ignores_www_slash_utm_and_keeps_first() -> None:
    items = [
        {"title": "A", "url": "https://www.example.com/post/"},
        {"title": "A copy", "url": "https://example.com/post?utm_source=x#frag"},
        {"title": "B", "url": "https://example.com/other"},
    ]
    result = dedupe(items=items, by="url")

    assert [i["title"] for i in result["items"]] == ["A", "B"]
    assert result["item_count"] == 2
    assert result["removed"] == 1


def test_dedupe_by_title_ignores_case_accents_and_spaces() -> None:
    items = [{"title": "Tin  AI hôm nay"}, {"title": "tin ai hom nay"}, {"title": "Khác"}]
    result = dedupe(items=items, by="title")

    assert result["item_count"] == 2
    assert result["removed"] == 1


def test_dedupe_keeps_items_missing_the_compared_field() -> None:
    result = dedupe(items=[{"title": "x"}, {"title": "y"}, {"url": ""}], by="url")
    assert result["item_count"] == 3
    assert result["removed"] == 0


def test_dedupe_empty_and_none_items_do_not_crash() -> None:
    assert dedupe(items=None)["item_count"] == 0
    assert dedupe(items=[])["item_count"] == 0


def test_dedupe_bad_by_returns_error_dict_instead_of_raising() -> None:
    result = dedupe(items=[{"url": "https://a.com"}], by="author")
    assert result["error"] == "ValueError"
    assert "items" not in result


def test_dedupe_non_list_items_returns_error_dict_instead_of_raising() -> None:
    result = dedupe(items="https://a.com")
    assert result["error"] == "TypeError"


def test_dedupe_by_url_treats_query_param_order_as_same_page() -> None:
    items = [{"url": "https://a.com/x?a=1&b=2"}, {"url": "https://a.com/x?b=2&a=1"}]
    assert dedupe(items=items)["item_count"] == 1


def test_dedupe_by_none_falls_back_to_url() -> None:
    items = [{"url": "https://a.com/x"}, {"url": "https://www.a.com/x/"}]
    result = dedupe(items=items, by=None)
    assert result["by"] == "url"
    assert result["item_count"] == 1
