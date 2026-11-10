from __future__ import annotations

from copy import deepcopy

import pytest

from agent import ResearchAgent
from providers.base import ModelResponse, ToolCall
from tools import TOOL_FUNCTIONS


deduplicate = TOOL_FUNCTIONS["deduplicate_sources"]


def test_empty_list_returns_zero_counts() -> None:
    assert deduplicate(items=[]) == {
        "tool": "deduplicate_sources", "items": [], "input_count": 0,
        "item_count": 0, "duplicates_removed": 0,
    }


@pytest.mark.parametrize("duplicate", [
    "https://EXAMPLE.com/news",
    "https://example.com:443/news",
    " https://example.com/news ",
    "https://example.com/news?utm_source=chat&utm_medium=email",
    "https://example.com/news?UTM_CAMPAIGN=test&fbclid=abc&gclid=xyz&dclid=x&msclkid=y",
])
def test_normalized_url_variants_are_duplicates(duplicate) -> None:
    original = {"url": "https://example.com/news"}
    result = deduplicate(items=[original, {"url": duplicate}])
    assert result["items"] == [original]
    assert result["duplicates_removed"] == 1


def test_empty_root_path_matches_slash() -> None:
    result = deduplicate(items=[{"url": "https://example.com"}, {"url": "https://example.com/"}])
    assert result["item_count"] == 1


@pytest.mark.parametrize("different", [
    "http://example.com/news?id=1",
    "https://example.com/News?id=1",
    "https://example.com/news/?id=1",
    "https://example.com/news?id=2",
    "https://example.com/news?id=1&page=",
    "https://example.com/news?id=1#section",
    "https://example.com:8443/news?id=1",
    "https://www.example.com/news?id=1",
])
def test_meaningful_url_differences_are_preserved(different) -> None:
    items = [{"url": "https://example.com/news?id=1"}, {"url": different}]
    result = deduplicate(items=items)
    assert result["items"] == items
    assert result["duplicates_removed"] == 0


def test_keeps_query_order_and_repeated_parameters() -> None:
    urls = [
        "https://example.com/?a=1&b=2", "https://example.com/?b=2&a=1",
        "https://example.com/?a=1&a=2", "https://example.com/?a=2&a=1",
    ]
    assert deduplicate(items=[{"url": url} for url in urls])["item_count"] == 4


def test_preserves_order_metadata_and_input_without_merging_by_title() -> None:
    items = [
        {"url": "https://example.com/a", "title": "Same", "extra": {"tags": ["ai"]}},
        {"url": "https://example.com/b", "title": "Same", "summary": "different source"},
        {"url": "https://example.com/a", "summary": "later metadata"},
    ]
    before = deepcopy(items)
    result = deduplicate(items=items)
    assert items == before
    assert result["items"] == before[:2]


@pytest.mark.parametrize("items", [None, {}, 3, [None], [{}], [{"url": ""}], [{"url": 123}]])
def test_missing_or_malformed_items_return_error_dict(items) -> None:
    result = deduplicate(items=items)
    assert result["tool"] == "deduplicate_sources"
    assert result["error"] == "ValueError"
    assert result["message"]
    assert "items" not in result


@pytest.mark.parametrize("url", [
    "/relative", "ftp://example.com/file", "https://", "https://example.com/bad path",
    "https://user:secret@example.com/", "https://example.com:bad/",
    "https://example.com:99999/", "https://[invalid/",
])
def test_invalid_url_returns_error_dict(url) -> None:
    assert deduplicate(items=[{"url": url}])["error"] == "ValueError"


def test_ipv6_default_port_can_be_deduplicated() -> None:
    assert deduplicate(items=[
        {"url": "http://[::1]:80/news"}, {"url": "http://[::1]/news"},
    ])["item_count"] == 1


def test_agent_dispatches_tool_and_result_can_be_formatted() -> None:
    items = [
        {"title": "First", "url": "https://example.com/a?utm_source=test"},
        {"title": "Duplicate", "url": "https://example.com/a"},
    ]

    class FakeProvider:
        def complete(self, messages, tools=None, **kwargs):
            return ModelResponse(text=None, tool_calls=[
                ToolCall("deduplicate_sources", {"items": items}),
            ])

    run = ResearchAgent(FakeProvider(), system_prompt="test").run([
        {"role": "user", "content": "Remove duplicate sources"},
    ])
    result = run.tool_results[0]["result"]
    assert result["duplicates_removed"] == 1
    digest = TOOL_FUNCTIONS["format"](items=result["items"], template="bullets")
    assert digest["item_count"] == 1
    assert "First" in digest["markdown"]
    assert "Duplicate" not in digest["markdown"]
