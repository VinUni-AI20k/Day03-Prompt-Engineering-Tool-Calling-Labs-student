from __future__ import annotations

import os
from contextlib import contextmanager
from contextvars import ContextVar
from typing import Any

import requests

from tools._shared import TIMEOUT

_approved_text: ContextVar[str | None] = ContextVar("telegram_approved_text", default=None)


@contextmanager
def approve_message(text: str):
    """Trusted UI only: enter after the user approves this exact message.

    Not registered as a model tool. Approval is consumed by one send attempt.
    """
    token = _approved_text.set(text)
    try:
        yield
    finally:
        _approved_text.reset(token)


def send_telegram(text: str = "", confirmed: bool = False) -> dict[str, Any]:
    if confirmed is not True or _approved_text.get() != text:
        return {
            "tool": "send_telegram",
            "status": "needs_confirmation",
            "message": "Only send after the user explicitly confirms.",
        }
    _approved_text.set(None)
    try:
        if not isinstance(text, str) or not text.strip() or len(text) > 4096:
            raise ValueError("text must contain 1-4096 characters")
        token = os.getenv("TELEGRAM_BOT_TOKEN")
        chat_id = os.getenv("TELEGRAM_CHAT_ID")
        if not token or not chat_id:
            raise RuntimeError("Missing TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID env var")
        response = requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={"chat_id": chat_id, "text": text},
            timeout=TIMEOUT,
        )
        response.raise_for_status()
        if response.json().get("ok") is not True:
            raise RuntimeError("Telegram did not acknowledge the message")
        return {"tool": "send_telegram", "status": "sent"}
    except Exception as exc:
        # requests exceptions may contain the bot token in the request URL.
        return {"tool": "send_telegram", "error": type(exc).__name__,
                "message": "Telegram send failed; check configuration, message and connection."}

