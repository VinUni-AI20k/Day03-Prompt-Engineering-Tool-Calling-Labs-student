"""Exercise Streamlit widgets offline; no model or Telegram calls."""
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest


@pytest.fixture
def ui(monkeypatch):
    import chat
    monkeypatch.setattr(chat, "write_transcript", lambda *args: None)
    app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py"))
    app.run(timeout=20)
    assert not app.exception
    return app


def button(app, label):
    return next(item for item in app.button if item.label == label)


def test_ui_deduplicate_runs_without_model(ui):
    button(ui, "Chạy tool").click().run()
    assert not ui.exception
    assert ui.session_state.events[0]["result"]["removed_count"] == 1


def test_ui_cancel_never_calls_send(ui, fake_http):
    from conftest import FakeResponse
    calls = fake_http(FakeResponse({"ok": True}))
    button(ui, "Xem trước gửi").click().run()
    assert ui.session_state.pending is not None
    button(ui, "Hủy gửi").click().run()
    assert not ui.exception
    assert ui.session_state.pending is None
    assert ui.session_state.events[0]["result"]["status"] == "cancelled"
    assert calls == []


def test_ui_demo_confirmation_never_calls_network(ui, fake_http):
    from conftest import FakeResponse
    calls = fake_http(FakeResponse({"ok": True}))
    button(ui, "Xem trước gửi").click().run()
    button(ui, "Xác nhận gửi").click().run()
    assert not ui.exception
    assert ui.session_state.pending is None
    assert ui.session_state.events[0]["result"]["status"] == "simulated"
    assert calls == []


def test_ui_real_send_uses_frozen_preview_once(ui, monkeypatch, fake_http):
    from conftest import FakeResponse
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "fake-token")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "123")
    calls = fake_http(FakeResponse({"ok": True}))
    ui.checkbox[0].uncheck().run()
    button(ui, "Xem trước gửi").click().run()
    expected = ui.session_state.pending["text"]
    ui.text_area[1].set_value("Changed after preview").run()
    button(ui, "Xác nhận gửi").click().run()
    assert not ui.exception
    assert len(calls) == 1
    assert calls[0]["json"]["text"] == expected
    ui.run()
    assert len(calls) == 1


def test_chat_model_cannot_bypass_confirmation(ui, monkeypatch, fake_http):
    from conftest import FakeResponse
    from providers.base import ModelResponse, ToolCall

    class FakeProvider:
        def complete(self, *args, **kwargs):
            return ModelResponse(tool_calls=[ToolCall("send", {"text": "Test message", "confirmed": True})])

    monkeypatch.setattr("providers.make_provider", lambda _: FakeProvider())
    calls = fake_http(FakeResponse({"ok": True}))
    ui.chat_input[0].set_value("Send Test message").run()
    assert not ui.exception
    assert ui.session_state.pending == {"text": "Test message", "demo": False}
    assert calls == []
    button(ui, "Hủy gửi").click().run()
    assert calls == []
