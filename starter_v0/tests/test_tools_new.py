"""Unit tests cho các tool do nhóm tự viết: hackernews, wikipedia, pypi_package.

(github_repo được test ở cuối test_tools_todo.py.) Offline: HTTP mock bằng `fake_http`.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest
import requests

from conftest import FakeResponse
from tools import TOOL_FUNCTIONS, load_tool_declarations

ROOT = Path(__file__).resolve().parents[1]
DECLARED = {item["name"] for item in load_tool_declarations(ROOT / "artifacts" / "tools.yaml")}
NEW_TOOLS_EVAL = ROOT / "data" / "eval_new_tools.json"
TEAM_TOOLS = ["github_repo", "hackernews", "wikipedia", "pypi_package"]


# ---------------- registry / eval coverage for team tools ----------------
# (kept here instead of test_tool_contract.py, which is the provided contract test)

def test_new_tools_eval_only_expects_declared_tools() -> None:
    data = json.loads(NEW_TOOLS_EVAL.read_text(encoding="utf-8"))
    for case in data["cases"]:
        for call in case.get("expect", {}).get("tool_calls", []):
            assert call["name"] in DECLARED, f"{case['id']} expects undeclared tool '{call['name']}'"


@pytest.mark.parametrize("name", TEAM_TOOLS)
def test_each_team_tool_has_an_eval_case_routing_to_it(name: str) -> None:
    data = json.loads(NEW_TOOLS_EVAL.read_text(encoding="utf-8"))
    routed = {call["name"] for case in data["cases"] for call in case["expect"].get("tool_calls", [])}
    assert name in routed, f"no case in eval_new_tools.json routes to '{name}'"

hackernews = TOOL_FUNCTIONS["hackernews"]
wikipedia = TOOL_FUNCTIONS["wikipedia"]
pypi_package = TOOL_FUNCTIONS["pypi_package"]


# ---------------- hackernews ----------------

def _hit(i: int, url: str | None = "https://example.com/a") -> dict:
    return {"objectID": str(i), "title": f"Story {i}", "url": url, "points": 10 * i, "num_comments": i,
            "created_at": "2026-01-01T00:00:00Z"}


def test_hackernews_happy_path_maps_hits_and_request(fake_http) -> None:
    calls = fake_http(FakeResponse({"hits": [_hit(1), _hit(2, url=None)]}))

    result = hackernews(query="rust async", sort="date", limit=2)

    assert calls[0]["url"] == "https://hn.algolia.com/api/v1/search_by_date"
    assert calls[0]["params"] == {"query": "rust async", "tags": "story", "hitsPerPage": 2}
    assert result["items"][0] == {
        "title": "Story 1", "url": "https://example.com/a", "source": "news.ycombinator.com",
        "summary": "10 points, 1 comments", "discussion_url": "https://news.ycombinator.com/item?id=1",
        "date": "2026-01-01T00:00:00Z",
    }
    # Ask HN không có url -> rơi về trang thảo luận
    assert result["items"][1]["url"] == "https://news.ycombinator.com/item?id=2"


def test_hackernews_skips_hits_without_title_or_id(fake_http) -> None:
    fake_http(FakeResponse({"hits": [{"objectID": "1", "title": None}, {"title": "no id"}, _hit(3)]}))

    items = hackernews(query="ai")["items"]

    assert [i["title"] for i in items] == ["Story 3"]


@pytest.mark.parametrize("bad", [{"query": ""}, {"query": "   "}, {"query": None}, {"query": "ai", "sort": "top"}])
def test_hackernews_bad_input_returns_error_without_http(bad, fake_http) -> None:
    calls = fake_http(FakeResponse({"hits": []}))

    result = hackernews(**bad)

    assert result["tool"] == "hackernews"
    assert result["error"] == "ValueError"
    assert calls == []


@pytest.mark.parametrize("limit, expected", [(0, 5), (-3, 5), (999, 20), ("7", 7)])
def test_hackernews_limit_is_clamped(limit, expected, fake_http) -> None:
    calls = fake_http(FakeResponse({"hits": []}))

    hackernews(query="ai", limit=limit)

    assert calls[0]["params"]["hitsPerPage"] == expected


def test_hackernews_http_error_returns_error_dict(fake_http) -> None:
    fake_http(FakeResponse(status_code=503))

    assert hackernews(query="ai")["error"] == "HTTPError"


# ---------------- wikipedia ----------------

WIKI_OK = {
    "type": "standard", "title": "Transformer (deep learning architecture)",
    "extract": "A transformer is a neural network.", "description": "Deep learning architecture",
    "content_urls": {"desktop": {"page": "https://en.wikipedia.org/wiki/Transformer_(deep_learning_architecture)"}},
}


def test_wikipedia_happy_path_encodes_title_and_maps_response(fake_http) -> None:
    calls = fake_http(FakeResponse(WIKI_OK))

    result = wikipedia(title="Transformer (deep learning architecture)")

    assert calls[0]["url"] == (
        "https://en.wikipedia.org/api/rest_v1/page/summary/Transformer_%28deep_learning_architecture%29"
    )
    assert result["items"][0]["summary"] == "A transformer is a neural network."
    assert result["items"][0]["source"] == "en.wikipedia.org"
    assert result["items"][0]["is_disambiguation"] is False


def test_wikipedia_vi_lang_and_disambiguation_flag(fake_http) -> None:
    calls = fake_http(FakeResponse({**WIKI_OK, "type": "disambiguation"}))

    result = wikipedia(title="Hà Nội", lang="vi")

    assert calls[0]["url"].startswith("https://vi.wikipedia.org/")
    assert result["items"][0]["is_disambiguation"] is True


@pytest.mark.parametrize("bad", [{"title": ""}, {"title": "  "}, {"title": 5}, {"title": "AI", "lang": "fr"}])
def test_wikipedia_bad_input_returns_error_without_http(bad, fake_http) -> None:
    calls = fake_http(FakeResponse(WIKI_OK))

    result = wikipedia(**bad)

    assert result["error"] == "ValueError"
    assert calls == []


def test_wikipedia_title_cannot_escape_path(fake_http) -> None:
    calls = fake_http(FakeResponse(WIKI_OK))

    wikipedia(title="../../etc/passwd?x=1#y")

    assert "/../" not in calls[0]["url"]
    assert "?" not in calls[0]["url"].split("summary/")[1]


@pytest.mark.parametrize("response, expected", [
    (FakeResponse(status_code=404), "HTTPError"),
    (requests.Timeout("slow"), "Timeout"),
    (FakeResponse(payload={"type": "x"}), "ValueError"),
])
def test_wikipedia_failure_returns_error_dict(response, expected, fake_http) -> None:
    fake_http(response)

    result = wikipedia(title="Anything")

    assert result["error"] == expected
    assert "items" not in result


# ---------------- pypi_package ----------------

PYPI_OK = {
    "info": {"name": "requests", "version": "2.32.0", "summary": "HTTP for Humans.",
             "requires_python": ">=3.8", "package_url": "https://pypi.org/project/requests/"},
    "urls": [{"upload_time_iso_8601": "2026-02-02T10:00:00Z"}],
}


def test_pypi_happy_path_maps_response(fake_http) -> None:
    calls = fake_http(FakeResponse(PYPI_OK))

    result = pypi_package(package="requests")

    assert calls[0]["url"] == "https://pypi.org/pypi/requests/json"
    assert result["items"][0] == {
        "title": "requests", "url": "https://pypi.org/project/requests/", "source": "pypi.org",
        "summary": "HTTP for Humans.", "latest_version": "2.32.0", "requires_python": ">=3.8",
        "released_at": "2026-02-02T10:00:00Z",
    }


@pytest.mark.parametrize("bad", ["", "  ", None, 7, "requests==2.0", "https://pypi.org/project/requests",
                                 "a/b", "../x", "-bad"])
def test_pypi_invalid_name_returns_error_without_http(bad, fake_http) -> None:
    calls = fake_http(FakeResponse(PYPI_OK))

    result = pypi_package(package=bad)

    assert result["tool"] == "pypi_package"
    assert result["error"] == "ValueError"
    assert calls == []


@pytest.mark.parametrize("response, expected", [
    (FakeResponse(status_code=404), "HTTPError"),
    (FakeResponse(status_code=429), "HTTPError"),
    (requests.Timeout("slow"), "Timeout"),
    (FakeResponse(payload={"info": {}}), "ValueError"),
    (FakeResponse(payload=[]), "ValueError"),
])
def test_pypi_failure_returns_error_dict(response, expected, fake_http) -> None:
    fake_http(response)

    result = pypi_package(package="requests")

    assert result["error"] == expected
    assert "items" not in result
