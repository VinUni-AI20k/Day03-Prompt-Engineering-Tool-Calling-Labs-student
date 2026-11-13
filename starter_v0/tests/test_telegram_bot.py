"""Offline tests for the Telegram chat bot: no network, no model calls."""
from __future__ import annotations

from typing import Any

import pytest

from telegram_bot import TelegramBot, parse_allowed, split_message


class RecordingBot(TelegramBot):
    """TelegramBot whose Telegram calls and agent turns are recorded instead of executed."""

    def __init__(self, allowed: set[int]) -> None:
        super().__init__("fake-token", allowed)
        self.calls: list[tuple[str, dict[str, Any]]] = []
        self.turns: list[tuple[int, str]] = []

    def call(self, method: str, **payload: Any) -> dict[str, Any]:
        self.calls.append((method, payload))
        return {"ok": True, "result": {}}

    def run_turn(self, chat_id: int, text: str) -> None:
        self.turns.append((chat_id, text))

    def texts(self) -> list[str]:
        return [p["text"] for m, p in self.calls if m == "sendMessage"]


def private_message(chat_id: int, text: str) -> dict[str, Any]:
    return {"chat": {"id": chat_id, "type": "private"}, "text": text}


def test_split_message_keeps_all_text_within_limit() -> None:
    text = "\n\n".join(f"Đoạn {i}: " + "nội dung " * 60 for i in range(30))
    chunks = split_message(text, limit=500)
    assert all(len(chunk) <= 500 for chunk in chunks)
    assert len(chunks) > 1
    assert "".join(chunks).replace("\n", "").replace(" ", "") == text.replace("\n", "").replace(" ", "")


def test_split_message_handles_empty_and_unbroken_text() -> None:
    assert split_message("   ") == ["(trống)"]
    assert [len(c) for c in split_message("x" * 9000, limit=4000)] == [4000, 4000, 1000]


@pytest.mark.parametrize("raw, expected", [
    (None, set()), ("", set()), ("123", {123}), ("123, -100456 ,abc, ", {123, -100456}),
])
def test_parse_allowed_ignores_junk(raw, expected) -> None:
    assert parse_allowed(raw) == expected


def test_unauthorized_chat_cannot_reach_the_agent() -> None:
    bot = RecordingBot(allowed={1})
    bot.handle_message(private_message(99, "Tin tức AI hôm nay"))
    assert bot.turns == []
    assert "chưa được cấp quyền" in bot.texts()[0]


def test_start_shows_chat_id_to_unauthorized_user() -> None:
    bot = RecordingBot(allowed=set())
    bot.handle_message(private_message(99, "/start"))
    assert bot.turns == []
    assert "99" in bot.texts()[0]


def test_authorized_text_runs_agent_turn() -> None:
    bot = RecordingBot(allowed={1})
    bot.handle_message(private_message(1, "Tin tức AI hôm nay"))
    assert bot.turns == [(1, "Tin tức AI hôm nay")]


def test_channel_posts_and_groups_are_ignored() -> None:
    bot = RecordingBot(allowed={1})
    bot.handle_message({"chat": {"id": 1, "type": "channel"}, "text": "hello"})
    bot.handle_message({"chat": {"id": 1, "type": "supergroup"}, "text": "hello"})
    assert bot.turns == [] and bot.calls == []


def test_confirm_button_sends_confirmation_text_and_removes_buttons() -> None:
    bot = RecordingBot(allowed={1})
    bot.handle_callback({"id": "cb", "data": "yn:yes", "message": {"chat": {"id": 1}, "message_id": 7}})
    assert bot.turns == [(1, "Có, đồng ý.")]
    methods = [m for m, _ in bot.calls]
    assert "editMessageReplyMarkup" in methods


def test_callback_from_unauthorized_chat_does_nothing() -> None:
    bot = RecordingBot(allowed={1})
    bot.handle_callback({"id": "cb", "data": "yn:yes", "message": {"chat": {"id": 99}, "message_id": 7}})
    assert bot.turns == []


def test_choice_button_maps_to_option_text() -> None:
    bot = RecordingBot(allowed={1})
    bot.pending_options[1] = ["Sam Altman", "Elon Musk"]
    bot.handle_callback({"id": "cb", "data": "opt:1", "message": {"chat": {"id": 1}, "message_id": 7}})
    assert bot.turns == [(1, "Elon Musk")]


def test_new_command_drops_the_session() -> None:
    bot = RecordingBot(allowed={1})
    bot.sessions[1] = {"id": "old"}
    bot.handle_message(private_message(1, "/new"))
    assert 1 not in bot.sessions
