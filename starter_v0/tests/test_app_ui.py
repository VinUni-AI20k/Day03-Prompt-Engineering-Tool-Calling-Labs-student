"""Offline tests for the Streamlit UI (app.py) with a fake provider.

No model/API call: providers.make_provider is replaced by a scripted fake, and
transcripts/artifacts live in a temp dir. Includes regression tests for the two
transcript issues found in Tân's review (MINH_CODE_REVIEW.md):
  1. config change mid-conversation must not leak old turns into the model context
  2. prompt/tools edited while the UI runs must be reflected in the recorded hash
"""
from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path
from typing import Any

import pytest
import streamlit as st
from streamlit.testing.v1 import AppTest

import chat
import providers
from providers.base import ModelResponse, ToolCall

ROOT = Path(__file__).resolve().parents[1]
APP = str(ROOT / "app.py")


class ScriptedProvider:
    """Returns queued responses (or a default text answer) and records every request."""

    default_model = "fake-model"

    def __init__(self, responses: list[ModelResponse | Exception] | None = None) -> None:
        self.responses = list(responses or [])
        self.requests: list[list[dict[str, str]]] = []

    def complete(self, messages, tools=None, **kwargs) -> ModelResponse:
        self.requests.append([dict(m) for m in messages])
        if self.responses:
            item = self.responses.pop(0)
            if isinstance(item, Exception):
                raise item
            return item
        return ModelResponse(text=f"answer #{len(self.requests)}", tool_calls=[])


@pytest.fixture
def ui_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Temp artifacts + transcripts dir and an injectable fake provider."""
    artifacts = tmp_path / "artifacts"
    artifacts.mkdir()
    shutil.copy(ROOT / "artifacts" / "system_prompt.md", artifacts / "system_prompt.md")
    shutil.copy(ROOT / "artifacts" / "tools.yaml", artifacts / "tools.yaml")
    monkeypatch.setattr(chat, "ARTIFACTS_DIR", artifacts)
    monkeypatch.setattr(chat, "ROOT", tmp_path)  # app.py: TRANSCRIPTS_DIR = ROOT / "transcripts"
    st.cache_resource.clear()

    def install(provider: ScriptedProvider) -> ScriptedProvider:
        monkeypatch.setattr(providers, "make_provider", lambda name: provider)
        return provider

    yield {"tmp": tmp_path, "artifacts": artifacts, "install": install}
    st.cache_resource.clear()


def send(at: AppTest, text: str) -> AppTest:
    at.chat_input[0].set_value(text).run()
    assert not at.exception, at.exception
    return at


def transcripts(tmp: Path) -> list[dict[str, Any]]:
    """All saved transcripts, oldest first (by the microsecond timestamp in transcript_id)."""
    data = [json.loads(f.read_text(encoding="utf-8")) for f in (tmp / "transcripts").glob("*.transcript.json")]
    return sorted(data, key=lambda t: t["transcript_id"].rsplit("_", 1)[-1])


def test_tool_call_is_shown_and_saved(ui_env) -> None:
    provider = ui_env["install"](ScriptedProvider([
        ModelResponse(text=None, tool_calls=[ToolCall(name="source_check", args={"items": [
            {"title": "Paper", "url": "https://arxiv.org/abs/1706.03762", "source": "arxiv.org"},
            {"title": "Thiếu nguồn"},
        ]})]),
        ModelResponse(text="1 item hợp lệ, 1 item thiếu URL và nguồn.", tool_calls=[]),
    ]))
    at = AppTest.from_file(APP, default_timeout=30).run()
    send(at, "Kiểm tra nguồn giúp mình")

    assistant = at.session_state["messages"][-1]
    assert assistant["status"] == "answered"
    event = assistant["rounds"][0]["tool_results"][0]
    assert event["tool"] == "source_check" and event["result"]["valid_count"] == 1
    assert "TOOL_RESULTS_JSON" in provider.requests[1][-1]["content"]
    assert any("Tool calls (1)" in e.label for e in at.expander)
    [saved] = transcripts(ui_env["tmp"])
    assert saved["interface"] == "streamlit" and saved["turns"][0]["status"] == "answered"


def test_provider_error_is_shown_not_raised(ui_env) -> None:
    ui_env["install"](ScriptedProvider([RuntimeError("simulated 429 RESOURCE_EXHAUSTED")]))
    at = AppTest.from_file(APP, default_timeout=30).run()
    send(at, "Tin AI hôm nay?")

    assert "simulated 429" in at.session_state["messages"][-1]["error"]
    assert len(at.error) == 1
    [saved] = transcripts(ui_env["tmp"])
    assert saved["turns"][0]["status"] == "provider_error"


def test_sample_question_button_sends_prompt(ui_env) -> None:
    ui_env["install"](ScriptedProvider())
    at = AppTest.from_file(APP, default_timeout=30).run()
    at.sidebar.button(key="sample_0").click().run()
    assert not at.exception, at.exception
    assert at.session_state["messages"][0]["content"] == "Tin tức AI hôm nay có gì nổi bật?"


def test_config_change_starts_new_conversation(ui_env) -> None:
    """Regression (review finding 1): old turns must not reach the model after a config change."""
    provider = ui_env["install"](ScriptedProvider())
    at = AppTest.from_file(APP, default_timeout=30).run()
    send(at, "lượt một")
    at.sidebar.text_input(key="cfg_version").set_value("changed-version").run()
    send(at, "lượt hai")

    second_request = provider.requests[-1]
    assert not any("lượt một" in m["content"] for m in second_request), "old turn leaked into model context"
    assert [m["content"] for m in at.session_state["messages"] if m["role"] == "user"] == ["lượt hai"]
    old, new = transcripts(ui_env["tmp"])
    assert [t["user"] for t in old["turns"]] == ["lượt một"]
    assert [t["user"] for t in new["turns"]] == ["lượt hai"]
    assert new["version"] == "changed-version"


def test_artifact_change_is_recorded_with_matching_hash(ui_env) -> None:
    """Regression (review finding 2): transcript hash must match the prompt actually sent."""
    provider = ui_env["install"](ScriptedProvider())
    prompt_file = ui_env["artifacts"] / "system_prompt.md"
    at = AppTest.from_file(APP, default_timeout=30).run()
    send(at, "lượt một")

    prompt_file.write_text(prompt_file.read_text(encoding="utf-8") + "\nNEW RULE FOR V2.\n", encoding="utf-8")
    send(at, "lượt hai")

    assert provider.requests[-1][0]["content"].endswith("NEW RULE FOR V2.\n")
    assert not any("lượt một" in m["content"] for m in provider.requests[-1])
    old, new = transcripts(ui_env["tmp"])
    expected_hash = hashlib.sha256(prompt_file.read_bytes()).hexdigest()
    assert new["prompt_hash"] == expected_hash != old["prompt_hash"]
    assert new["turns"][0]["artifact_version"] == new["artifact_version"]
    assert old["turns"][0]["artifact_version"] == old["artifact_version"]
