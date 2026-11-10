"""Tool Unit Test Challenge (CP3) - tests cho các tool có sẵn của starter.

Offline only: HTTP được mock bằng `fake_http`, key giả đặt bằng `monkeypatch.setenv`.
Mỗi test kiểm tra một hành vi. Mục `YOUR NEW TOOL(S)` ở cuối file thuộc về người viết tool mới.
"""
from __future__ import annotations

import pytest
import requests

from conftest import FakeResponse
from tools import TOOL_FUNCTIONS

clarify_tool = TOOL_FUNCTIONS["clarify"]
format_tool = TOOL_FUNCTIONS["format"]
send_tool = TOOL_FUNCTIONS["send"]
lookup_tool = TOOL_FUNCTIONS["lookup"]
fetch_tool = TOOL_FUNCTIONS["fetch"]
timeline_tool = TOOL_FUNCTIONS["timeline"]
social_search_tool = TOOL_FUNCTIONS["social_search"]
policy_tool = TOOL_FUNCTIONS["policy"]
papers_tool = TOOL_FUNCTIONS["papers"]
paper_text_tool = TOOL_FUNCTIONS["paper_text"]


def _tweets(count: int, handle: str = "sama") -> list[dict]:
    return [{"tweet_id": str(1000 + i), "screen_name": handle, "text": f"tweet {i}"} for i in range(count)]


# ---------------- clarify ----------------

def test_clarify_choice_returns_options_and_awaits_user() -> None:
    result = clarify_tool(question="Chọn nguồn?", response_type="choice", options=["web", "x"])

    assert result["options"] == ["web", "x"]
    assert result["response_type"] == "choice"
    assert result["question"] == "Chọn nguồn?"
    assert result["awaiting_user"] is True


def test_clarify_without_options_defaults_to_empty_list() -> None:
    result = clarify_tool(question="Tài khoản nào?")

    assert result["options"] == []
    assert result["response_type"] == "text"
    assert result["awaiting_user"] is True


# ---------------- format ----------------

def test_format_sections_groups_items_by_section() -> None:
    items = [
        {"title": "a1", "section": "A"},
        {"title": "b1", "section": "B"},
        {"title": "a2", "section": "A"},
    ]
    markdown = format_tool(items=items, template="sections")["markdown"]

    assert markdown.count("## A") == 1
    assert markdown.count("## B") == 1
    assert markdown.index("a1") < markdown.index("a2") < markdown.index("b1")


def test_format_thread_numbers_items() -> None:
    items = [{"title": f"tin {i}", "url": f"https://example.com/{i}"} for i in range(3)]
    lines = format_tool(items=items, template="thread")["markdown"].split("\n\n")

    assert [line.split(" ")[0] for line in lines] == ["1/", "2/", "3/"]


def test_format_empty_items_does_not_crash() -> None:
    for empty in (None, []):
        result = format_tool(items=empty, template="sections")
        assert result["item_count"] == 0


def test_format_item_without_url_has_no_link_markup() -> None:
    markdown = format_tool(items=[{"title": "Không có link"}], template="bullets")["markdown"]

    assert "Không có link" in markdown
    assert "](" not in markdown


# ---------------- send (guardrail) ----------------

def test_send_confirmed_posts_to_telegram(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "tok123")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "-10042")
    calls = fake_http(FakeResponse({"ok": True}))

    result = send_tool(text="Bản tin AI", confirmed=True)

    assert len(calls) == 1
    assert calls[0]["method"] == "POST"
    assert "tok123" in calls[0]["url"]
    assert calls[0]["json"]["chat_id"] == "-10042"
    assert calls[0]["json"]["text"] == "Bản tin AI"
    assert result["status"] == "sent"


def test_send_confirmed_without_env_returns_error_and_no_request(fake_http) -> None:
    calls = fake_http(FakeResponse({"ok": True}))

    result = send_tool(text="Bản tin", confirmed=True)

    assert result["error"] == "RuntimeError"
    assert "TELEGRAM_BOT_TOKEN" in result["message"]
    assert calls == []


def test_send_telegram_http_error_returns_error_dict(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "tok123")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "-10042")
    fake_http(FakeResponse(status_code=429))

    assert send_tool(text="x", confirmed=True)["error"] == "HTTPError"


def test_send_string_false_is_not_treated_as_confirmation(monkeypatch, fake_http) -> None:
    # Regression: model đôi khi gửi confirmed="false" (chuỗi). Chuỗi không rỗng là truthy
    # nên bản cũ gửi tin đi dù user chưa xác nhận.
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "tok123")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "-10042")
    calls = fake_http(FakeResponse({"ok": True}))

    result = send_tool(text="Bản tin", confirmed="false")

    assert result["status"] == "needs_confirmation"
    assert calls == []


def test_send_default_is_not_confirmed_and_makes_no_request(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "tok123")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "-10042")
    calls = fake_http(FakeResponse({"ok": True}))

    result = send_tool(text="Bản tin")  # model quên truyền confirmed

    assert result["status"] == "needs_confirmation"
    assert calls == []


def test_send_error_message_does_not_leak_bot_token(monkeypatch, fake_http) -> None:
    # Regression: lỗi của requests chứa nguyên URL (có token bot) -> token lọt vào kết quả tool,
    # tức là vào transcript và UI.
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "SECRET123:abc")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "-10042")
    fake_http(requests.ConnectionError("Max retries exceeded with url: /botSECRET123:abc/sendMessage"))

    result = send_tool(text="x", confirmed=True)

    assert result["error"] == "ConnectionError"
    assert "SECRET123" not in str(result)


# ---------------- lookup ----------------

def test_lookup_without_timeframe_omits_time_range(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("TAVILY_API_KEY", "test-key")
    calls = fake_http(FakeResponse({"results": []}))

    lookup_tool(query="AI", timeframe=None)

    assert "time_range" not in calls[0]["json"]


def test_lookup_numeric_string_max_results_is_coerced(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("TAVILY_API_KEY", "test-key")
    calls = fake_http(FakeResponse({"results": []}))

    result = lookup_tool(query="AI", max_results="5")

    assert calls[0]["json"]["max_results"] == 5
    assert "error" not in result


def test_lookup_non_numeric_max_results_returns_error_dict(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("TAVILY_API_KEY", "test-key")
    calls = fake_http(FakeResponse({"results": []}))

    result = lookup_tool(query="AI", max_results="nhiều")

    assert result["error"] == "ValueError"
    assert calls == []


def test_lookup_without_key_returns_error_and_no_request(fake_http) -> None:
    calls = fake_http(FakeResponse({"results": []}))

    result = lookup_tool(query="AI")

    assert result["error"] == "RuntimeError"
    assert "TAVILY_API_KEY" in result["message"]
    assert calls == []


# ---------------- fetch ----------------

def test_fetch_maps_firecrawl_response(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("FIRECRAWL_API_KEY", "fc-key")
    calls = fake_http(FakeResponse({"data": {
        "markdown": "# Nội dung",
        "metadata": {"title": "T", "sourceURL": "https://www.openai.com/blog/x"},
    }}))

    result = fetch_tool(url="https://www.openai.com/blog/x")

    assert calls[0]["url"] == "https://api.firecrawl.dev/v1/scrape"
    assert calls[0]["json"]["url"] == "https://www.openai.com/blog/x"
    assert calls[0]["headers"]["Authorization"] == "Bearer fc-key"
    assert result["items"][0] == {
        "title": "T", "url": "https://www.openai.com/blog/x",
        "source": "openai.com", "summary": "# Nội dung",
    }


def test_fetch_truncates_markdown_to_4000_chars(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("FIRECRAWL_API_KEY", "fc-key")
    fake_http(FakeResponse({"data": {"markdown": "x" * 5000, "metadata": {}}}))

    result = fetch_tool(url="https://example.com/long")

    assert len(result["items"][0]["summary"]) == 4000
    assert result["items"][0]["title"] == "https://example.com/long"


def test_fetch_without_key_returns_error_dict(fake_http) -> None:
    calls = fake_http(FakeResponse({}))

    result = fetch_tool(url="https://example.com")

    assert result["error"] == "RuntimeError"
    assert "FIRECRAWL_API_KEY" in result["message"]
    assert calls == []


# ---------------- timeline / social_search ----------------

def test_timeline_respects_limit_and_skips_items_without_id(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("RAPIDAPI_KEY", "rk")
    raw = [{"screen_name": "sama", "text": "no id"}] + _tweets(6)
    calls = fake_http(FakeResponse({"timeline": raw}))

    result = timeline_tool(screenname="sama", limit=3)

    assert calls[0]["params"] == {"screenname": "sama"}
    assert calls[0]["headers"]["x-rapidapi-key"] == "rk"
    assert len(result["items"]) == 3
    assert result["items"][0]["url"] == "https://x.com/sama/status/1000"
    assert all(item["url"].startswith("https://x.com/sama/status/") for item in result["items"])


def test_timeline_numeric_string_limit_is_coerced(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("RAPIDAPI_KEY", "rk")
    fake_http(FakeResponse({"timeline": _tweets(6)}))

    assert len(timeline_tool(screenname="sama", limit="2")["items"]) == 2


@pytest.mark.parametrize("bad_limit", [0, -1])
def test_timeline_non_positive_limit_falls_back_to_default(monkeypatch, fake_http, bad_limit) -> None:
    # Regression: limit=-1 từng thành items[:-1] (bỏ tweet cuối, trả gần hết danh sách).
    monkeypatch.setenv("RAPIDAPI_KEY", "rk")
    fake_http(FakeResponse({"timeline": _tweets(8)}))

    assert len(timeline_tool(screenname="sama", limit=bad_limit)["items"]) == 5


def test_timeline_without_key_returns_error_dict(fake_http) -> None:
    calls = fake_http(FakeResponse({"timeline": []}))

    result = timeline_tool(screenname="sama")

    assert result["error"] == "RuntimeError"
    assert "RAPIDAPI_KEY" in result["message"]
    assert calls == []


@pytest.mark.parametrize("search_type", ["Top", "Latest"])
def test_social_search_passes_search_type(monkeypatch, fake_http, search_type) -> None:
    monkeypatch.setenv("RAPIDAPI_KEY", "rk")
    calls = fake_http(FakeResponse({"timeline": _tweets(2)}))

    result = social_search_tool(query="GPT-5", search_type=search_type)

    assert calls[0]["params"] == {"query": "GPT-5", "search_type": search_type}
    assert result["search_type"] == search_type
    assert len(result["items"]) == 2


@pytest.mark.parametrize("bad_limit", [0, -1])
def test_social_search_non_positive_limit_falls_back_to_default(monkeypatch, fake_http, bad_limit) -> None:
    monkeypatch.setenv("RAPIDAPI_KEY", "rk")
    fake_http(FakeResponse({"timeline": _tweets(8)}))

    assert len(social_search_tool(query="AI", limit=bad_limit)["items"]) == 5


def test_social_search_http_error_returns_error_dict(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("RAPIDAPI_KEY", "rk")
    fake_http(FakeResponse(status_code=429))

    assert social_search_tool(query="AI")["error"] == "HTTPError"


# ---------------- policy (local knowledge + trust boundary) ----------------

def test_policy_empty_query_returns_no_results() -> None:
    assert policy_tool(query="")["results"] == []
    assert policy_tool(query="   ")["results"] == []


def test_policy_area_filter_only_returns_that_area() -> None:
    results = policy_tool(query="data privacy personal information", policy_area="data_privacy", top_k=10)["results"]

    assert results
    assert {item["policy_area"] for item in results} == {"data_privacy"}


def test_policy_top_k_limits_results() -> None:
    results = policy_tool(query="policy source tool data", policy_area="all", top_k=2)["results"]

    assert 1 <= len(results) <= 2


def test_policy_non_positive_top_k_still_returns_at_least_one_result() -> None:
    assert len(policy_tool(query="citation source", top_k=-5)["results"]) >= 1


def test_policy_instruction_like_lines_go_to_untrusted_text() -> None:
    result = policy_tool(query="injection probe citation viral", policy_area="source_citation", top_k=10)
    probe = [item for item in result["results"] if item["section"] == "Injection probe"]

    assert probe, "section 'Injection probe' phải được tìm thấy"
    assert any("ignore the citation policy" in line for line in probe[0]["untrusted_text"])
    assert "ignore the citation policy" not in probe[0]["facts"]
    assert "untrusted" in result["trust_boundary"].lower()


# ---------------- github_repo (tool mới của nhóm) ----------------
# Mỗi tool mới có đủ 3 loại test: happy path, input xấu từ model, lỗi API -> error dict.

def test_github_repo_maps_response_and_sends_expected_request(fake_http):
    calls = fake_http(FakeResponse({
        "full_name": "psf/requests",
        "html_url": "https://github.com/psf/requests",
        "description": "HTTP library",
        "stargazers_count": 123,
        "forks_count": 45,
        "language": "Python",
        "updated_at": "2026-01-01T00:00:00Z",
    }))

    result = TOOL_FUNCTIONS["github_repo"](repo="psf/requests")

    assert len(calls) == 1
    assert calls[0]["method"] == "GET"
    assert calls[0]["url"] == "https://api.github.com/repos/psf/requests"
    assert calls[0]["headers"]["Accept"] == "application/vnd.github+json"
    assert calls[0]["timeout"] > 0
    assert result == {
        "tool": "github_repo",
        "items": [{
            "title": "psf/requests",
            "url": "https://github.com/psf/requests",
            "source": "github.com",
            "summary": "HTTP library",
            "stars": 123,
            "forks": 45,
            "language": "Python",
            "updated_at": "2026-01-01T00:00:00Z",
        }],
    }


@pytest.mark.parametrize("repo", [
    "", "   ", None, 123, "requests", "psf/..",
    "https://github.com/psf/requests", "psf/requests.git",
])
def test_github_repo_invalid_input_returns_error_without_http(repo, fake_http):
    calls = fake_http(FakeResponse({}))

    result = TOOL_FUNCTIONS["github_repo"](repo=repo)

    assert result["tool"] == "github_repo"
    assert result["error"] == "ValueError"
    assert result["message"]
    assert calls == []


@pytest.mark.parametrize("response, expected_error", [
    (FakeResponse(status_code=403), "HTTPError"),
    (FakeResponse(status_code=404), "HTTPError"),
    (FakeResponse(status_code=429), "HTTPError"),
    (requests.Timeout("Request timed out"), "Timeout"),
    (FakeResponse(payload=[]), "ValueError"),
])
def test_github_repo_api_failure_returns_error_dict(response, expected_error, fake_http):
    calls = fake_http(response)

    result = TOOL_FUNCTIONS["github_repo"](repo="psf/requests")

    assert len(calls) == 1
    assert result["tool"] == "github_repo"
    assert result["error"] == expected_error
    assert result["message"]
    assert "items" not in result


# ---------------- papers / paper_text ----------------

ATOM_FEED = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom"
      xmlns:opensearch="http://a9.com/-/spec/opensearch/1.1/"
      xmlns:arxiv="http://arxiv.org/schemas/atom">
  <opensearch:totalResults>4798</opensearch:totalResults>
  <entry>
    <id>http://arxiv.org/abs/2401.04088v1</id>
    <title>Mixtral of
      Experts</title>
    <summary>A sparse
      mixture of experts model.</summary>
    <published>2024-01-08T00:00:00Z</published>
    <updated>2024-01-08T00:00:00Z</updated>
    <author><name>Albert Jiang</name></author>
    <link href="http://arxiv.org/pdf/2401.04088v1" rel="related" title="pdf"/>
    <arxiv:primary_category term="cs.LG"/>
    <category term="cs.LG"/>
  </entry>
</feed>"""


@pytest.fixture
def no_arxiv_sleep(monkeypatch):
    """arXiv tools sleep between requests; skip the waiting in tests."""
    monkeypatch.setattr("tools.papers.tool.time.sleep", lambda _s: None)
    monkeypatch.setattr("tools.paper_text.tool.time.sleep", lambda _s: None)


def test_papers_maps_atom_feed_and_sends_expected_request(fake_http, no_arxiv_sleep) -> None:
    calls = fake_http(FakeResponse(text=ATOM_FEED))

    result = papers_tool(query="mixture of experts", max_results=3)

    assert calls[0]["url"] == "https://export.arxiv.org/api/query"
    assert calls[0]["params"]["search_query"] == "all:mixture AND all:experts"
    assert calls[0]["params"]["max_results"] == 3
    assert result["total_results"] == 4798
    paper = result["items"][0]
    assert paper["arxiv_id"] == "2401.04088v1"
    assert paper["title"] == "Mixtral of Experts"  # xuống dòng trong XML được gộp lại
    assert paper["summary"] == "A sparse mixture of experts model."
    assert paper["authors"] == ["Albert Jiang"]
    assert paper["pdf_url"] == "http://arxiv.org/pdf/2401.04088v1"


@pytest.mark.parametrize(("given", "expected"), [(0, 5), (-5, 1), (99, 10), ("abc", None)])
def test_papers_max_results_is_clamped_or_rejected(given, expected, fake_http, no_arxiv_sleep) -> None:
    calls = fake_http(FakeResponse(text=ATOM_FEED))

    result = papers_tool(query="transformer", max_results=given)

    if expected is None:
        assert result["error"] == "ValueError"
        assert calls == []
    else:
        assert calls[0]["params"]["max_results"] == expected


def test_papers_rate_limited_returns_error_dict_after_retries(fake_http, no_arxiv_sleep) -> None:
    calls = fake_http(FakeResponse(status_code=429))

    result = papers_tool(query="transformer")

    assert result["error"] == "HTTPError"
    assert len(calls) == 3  # thử lại 3 lần rồi mới bỏ cuộc


def test_papers_malformed_xml_returns_error_dict(fake_http, no_arxiv_sleep) -> None:
    fake_http(FakeResponse(text="<feed><entry>"))

    assert papers_tool(query="transformer")["error"] == "ParseError"


@pytest.mark.parametrize("bad_url", ["", "not an arxiv id", "https://example.com/paper.pdf"])
def test_paper_text_invalid_id_returns_error_without_http(bad_url, fake_http, no_arxiv_sleep) -> None:
    calls = fake_http(FakeResponse(content=b"%PDF"))

    result = paper_text_tool(arxiv_url=bad_url)

    assert result["error"] == "ValueError"
    assert calls == []


def test_paper_text_download_failure_returns_error_dict(fake_http, no_arxiv_sleep) -> None:
    fake_http(FakeResponse(status_code=404))

    assert paper_text_tool(arxiv_url="https://arxiv.org/abs/2401.04088")["error"] == "HTTPError"


@pytest.mark.parametrize(
    ("query", "expected"),
    [
        ("mixture of experts", "all:mixture AND all:experts"),
        ("attention in the transformer", "all:attention AND all:transformer"),
        ("of the", "all:of AND all:the"),  # only stopwords: keep them rather than send an empty query
        ("au:hinton", "au:hinton"),  # field syntax is passed through untouched
    ],
)
def test_papers_search_query_drops_stopwords(query, expected):
    # Regression: arXiv ANDs every term, so "of" made "mixture of experts" return 0 results.
    from tools.papers.tool import _arxiv_search_query

    assert _arxiv_search_query(query) == expected
