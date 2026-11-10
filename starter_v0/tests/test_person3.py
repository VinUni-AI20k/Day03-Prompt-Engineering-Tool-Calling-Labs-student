"""Offline tests for Person 3; never send real Telegram messages."""
from copy import deepcopy

import pytest
import requests

from conftest import FakeResponse
from providers.base import ToolCall
from tools import TOOL_FUNCTIONS
from tools.send.tool import approve_message, send_telegram


def test_deduplicate_preserves_first_item_without_mutation():
    items = [{"url": "https://example.com/a?utm_source=x", "title": "First"},
             {"url": "https://EXAMPLE.com/a#section", "title": "Second"},
             {"url": "https://example.com/a?id=2"}]
    original = deepcopy(items)
    result = TOOL_FUNCTIONS["deduplicate"](items)
    assert result["items"] == [items[0], items[2]]
    assert result["removed_count"] == 1
    assert items == original


@pytest.mark.parametrize("items", [None, "wrong", [1], [{"url": "file:///etc/passwd"}],
                                      [{"url": "https://example.com:bad"}], [{}] * 101])
def test_deduplicate_bad_input_returns_error(items):
    assert "error" in TOOL_FUNCTIONS["deduplicate"](items)


def test_deduplicate_empty_input():
    assert TOOL_FUNCTIONS["deduplicate"]([])["items"] == []


def test_citation_audit_valid_metadata():
    assert TOOL_FUNCTIONS["citation_audit"]([
        {"title": "Paper", "source": "arxiv.org", "url": "https://arxiv.org/abs/1234.56789"}
    ])["passed"] is True


def test_citation_audit_reports_specific_issues():
    result = TOOL_FUNCTIONS["citation_audit"]([
        {"title": "A", "source": "Example", "url": "https://example.com"},
        {"title": "B", "source": "Example", "url": "https://example.com/#x"},
        {"url": "javascript:alert(1)"}])
    assert result["passed"] is False
    assert result["issues"][0] == {"index": 1, "problems": ["duplicate_url"]}
    assert set(result["issues"][1]["problems"]) == {"missing_title", "missing_source", "invalid_url"}


@pytest.mark.parametrize("items", [None, "bad", [1], [{}] * 101])
def test_citation_audit_invalid_collection_returns_error(items):
    assert "error" in TOOL_FUNCTIONS["citation_audit"](items)


@pytest.mark.parametrize("confirmed", [False, True, "true", "false", 1])
def test_model_cannot_authorize_send(confirmed, fake_http):
    calls = fake_http(FakeResponse({"ok": True}))
    assert send_telegram("Hello", confirmed)["status"] == "needs_confirmation"
    assert calls == []


def test_approval_is_bound_to_text_and_consumed(monkeypatch, fake_http):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "fake-token")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "123")
    calls = fake_http(FakeResponse({"ok": True}))
    with approve_message("Hello"):
        assert send_telegram("Changed", True)["status"] == "needs_confirmation"
        assert send_telegram("Hello", True)["status"] == "sent"
        assert send_telegram("Hello", True)["status"] == "needs_confirmation"
    assert len(calls) == 1
    assert calls[0]["json"] == {"chat_id": "123", "text": "Hello"}
    assert send_telegram("Hello", True)["status"] == "needs_confirmation"


def test_approved_send_missing_config_has_no_network(fake_http):
    calls = fake_http(FakeResponse({"ok": True}))
    with approve_message("Hello"):
        assert "error" in send_telegram("Hello", True)
    assert calls == []


@pytest.mark.parametrize("response", [FakeResponse({"ok": False}), FakeResponse(status_code=500),
                                     requests.Timeout("secret-token-in-url")])
def test_telegram_failures_are_sanitized(monkeypatch, fake_http, response):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "fake-token")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "123")
    fake_http(response)
    with approve_message("Hello"):
        result = send_telegram("Hello", True)
    assert "error" in result
    assert "secret-token" not in str(result)


@pytest.mark.parametrize("answer", ["no", "SEND"])
def test_cli_requires_explicit_confirmation(monkeypatch, fake_http, answer):
    from chat import execute_tool_call
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "fake-token")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "123")
    monkeypatch.setattr("builtins.input", lambda _: answer)
    calls = fake_http(FakeResponse({"ok": True}))
    result = execute_tool_call(ToolCall("send", {"text": "Hello", "confirmed": True}))
    assert result["result"]["status"] == ("sent" if answer == "SEND" else "cancelled")
    assert len(calls) == (1 if answer == "SEND" else 0)
