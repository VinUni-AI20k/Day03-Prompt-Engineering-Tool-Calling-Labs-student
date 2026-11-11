"""Offline regression tests for CP4–CP5 chat transcript persistence."""
from __future__ import annotations

import builtins
import json
import sys
from pathlib import Path

import chat
from providers.base import ModelResponse


class SuccessfulProvider:
    default_model = "fake-model"

    def complete(self, messages, tools=None, *, model=None, temperature=0.0, tool_choice=None) -> ModelResponse:
        return ModelResponse(text="Saved answer")


class FailingProvider:
    default_model = "fake-model"

    def complete(self, messages, tools=None, *, model=None, temperature=0.0, tool_choice=None) -> ModelResponse:
        raise RuntimeError("simulated provider outage")


def run_chat_once(monkeypatch, tmp_path: Path, provider) -> dict:
    answers = iter(["Test prompt", "/exit"])
    monkeypatch.setattr(builtins, "input", lambda _prompt: next(answers))
    monkeypatch.setattr(chat, "make_provider", lambda _name: provider)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "chat.py",
            "--provider",
            "openrouter",
            "--version",
            "test",
            "--transcripts-dir",
            str(tmp_path),
        ],
    )

    chat.main()

    files = list(tmp_path.glob("*.transcript.json"))
    assert len(files) == 1
    assert not list(tmp_path.glob("*.tmp"))
    return json.loads(files[0].read_text(encoding="utf-8"))


def test_chat_saves_complete_transcript_after_successful_response(monkeypatch, tmp_path: Path) -> None:
    transcript = run_chat_once(monkeypatch, tmp_path, SuccessfulProvider())

    assert transcript["turns"][0]["status"] == "answered"
    assert transcript["turns"][0]["assistant_text"] == "Saved answer"
    assert transcript["updated_at"]


def test_chat_saves_complete_transcript_after_provider_error(monkeypatch, tmp_path: Path) -> None:
    transcript = run_chat_once(monkeypatch, tmp_path, FailingProvider())

    turn = transcript["turns"][0]
    assert turn["status"] == "provider_error"
    assert "RuntimeError: simulated provider outage" == turn["error"]
    assert turn["ended_at"]
