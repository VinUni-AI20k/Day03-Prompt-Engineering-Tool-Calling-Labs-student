from __future__ import annotations

import json
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from providers.base import ModelResponse, ToolCall
from ui_support import new_session, run_turn, transcript_json


class ScriptedProvider:
    def __init__(self, responses):
        self.responses = iter(responses)
        self.messages = []

    def complete(self, messages, tools=None, **kwargs):
        self.messages.append(messages)
        return next(self.responses)


def test_ui_uses_main_dedup_strategy_and_keeps_followup_history(tmp_path):
    session = new_session()
    provider = ScriptedProvider([
        ModelResponse(tool_calls=[ToolCall("clarify", {"question": "Bạn gửi danh sách nguồn nhé?"})]),
        ModelResponse(tool_calls=[ToolCall("deduplicate_sources", {
            "items": [{"url": "https://example.com/a"}, {"url": "https://example.com/a?utm_source=x"}],
            "strategy": "url",
        })]),
        ModelResponse(text="Còn một nguồn."),
    ])
    run_turn(session, "Loại trùng giúp tôi", provider, directory=tmp_path)
    assert session["turns"][0]["status"] == "waiting_for_user"
    run_turn(session, "Hai URL cùng bài ở đây", provider, directory=tmp_path)
    assert provider.messages[1][1]["content"] == "Loại trùng giúp tôi"
    result = session["turns"][1]["tool_events"][0]["result"]
    assert result["unique_count"] == 1
    assert result["strategy"] == "url"
    saved = json.loads(next(tmp_path.glob("*.json")).read_text(encoding="utf-8"))
    assert saved["turns"][1]["assistant_text"] == "Còn một nguồn."
    assert len(new_session()["turns"]) == 0


def test_provider_failure_redacts_saved_and_downloaded_credentials(tmp_path, monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "private-test-secret")

    class BrokenProvider:
        def complete(self, *args, **kwargs):
            raise RuntimeError("Request failed private-test-secret")

    session = new_session()
    run_turn(session, "Tìm nguồn", BrokenProvider(), directory=tmp_path)
    assert session["turns"][0]["status"] == "provider_error"
    assert "[REDACTED]" in session["turns"][0]["error"]
    assert "private-test-secret" not in transcript_json(session)
    assert "private-test-secret" not in next(tmp_path.glob("*.json")).read_text()


def test_ui_rejects_changed_artifacts_and_turn_limit(tmp_path, monkeypatch):
    import ui_support

    session = new_session()
    with pytest.raises(ValueError, match="6000"):
        run_turn(session, "x" * 6001, None, directory=tmp_path)
    altered = tmp_path / "prompt.md"
    altered.write_text("different prompt", encoding="utf-8")
    monkeypatch.setattr(ui_support, "PROMPT", altered)
    with pytest.raises(ValueError, match="đã đổi"):
        run_turn(session, "hello", None, directory=tmp_path)
    session["turns"] = [{}] * 20
    with pytest.raises(ValueError, match="20 lượt"):
        run_turn(session, "hello", None, directory=tmp_path)


def test_app_clarification_reset_and_fourteen_tools(tmp_path, monkeypatch):
    import providers
    import ui_support

    monkeypatch.delenv("DEMO_ACCESS_CODE", raising=False)
    provider = ScriptedProvider([
        ModelResponse(tool_calls=[ToolCall("clarify", {"question": "Bạn cần tài khoản nào?"})]),
    ])
    original = ui_support.run_turn
    monkeypatch.setattr(ui_support, "run_turn", lambda s, t, p: original(s, t, p, directory=tmp_path))
    monkeypatch.setattr(providers, "make_provider", lambda name: provider)
    app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py")).run()
    assert not app.exception
    assert app.metric[0].value == "14"
    app.chat_input[0].set_value("Lấy bài đăng mới nhất").run()
    assert not app.exception
    assert "Bạn cần tài khoản nào?" in [m.value for m in app.markdown]
    old_id = app.session_state["conversation"]["transcript_id"]
    app.button(key="reset").click().run()
    assert not app.exception
    assert app.session_state["conversation"]["transcript_id"] != old_id
    assert app.session_state["conversation"]["turns"] == []
    assert (tmp_path / f"{old_id}.transcript.json").exists()


def test_app_access_code_blocks_chat_until_authorized(monkeypatch):
    monkeypatch.setenv("DEMO_ACCESS_CODE", "team-test-code")
    app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py")).run()
    assert not app.chat_input
    app.text_input(key="access_code").set_value("wrong")
    app.button(key="unlock").click().run()
    assert app.error[0].value == "Mã chưa đúng."
    assert not app.chat_input
    app.text_input(key="access_code").set_value("team-test-code")
    app.button(key="unlock").click().run()
    assert not app.exception
    assert len(app.chat_input) == 1
