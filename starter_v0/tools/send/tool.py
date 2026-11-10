from __future__ import annotations

import os
from typing import Any

import requests

from tools._shared import TIMEOUT, err


def _is_confirmed(value: Any) -> bool:
    """Strict check: only a real True (or the literal string "true") counts as confirmation.

    Bug fixed (regression test in tests/test_tools_todo.py): the old code used
    `if not confirmed`, so a model that sent the STRING "false" (truthy) posted to Telegram.
    """
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() == "true"
    return False


CONNECTION_ATTEMPTS = 2


def _post(token: str, chat_id: str, text: str, parse_mode: str | None) -> requests.Response:
    payload: dict[str, Any] = {"chat_id": chat_id, "text": text}
    if parse_mode:
        payload["parse_mode"] = parse_mode
    # Our network resets ~1/8 TLS connections to api.telegram.org (ConnectionResetError 10054,
    # see transcripts/v3_openrouter_20261111T000200284279.transcript.json). Retry ONCE on a
    # connection-level error only. Risk: if the reset happened after Telegram accepted the
    # message, it can be posted twice; HTTP errors (4xx/5xx) are never retried here.
    for attempt in range(CONNECTION_ATTEMPTS):
        try:
            return requests.post(
                f"https://api.telegram.org/bot{token}/sendMessage",
                json=payload,
                timeout=TIMEOUT,
            )
        except requests.ConnectionError:
            if attempt == CONNECTION_ATTEMPTS - 1:
                raise
    raise RuntimeError("unreachable")


def send_telegram(text: str = "", confirmed: bool = False) -> dict[str, Any]:
    if not _is_confirmed(confirmed):
        return {
            "tool": "send_telegram",
            "status": "needs_confirmation",
            "message": "Only send after the user explicitly confirms.",
        }
    try:
        if not isinstance(text, str) or not text.strip():
            raise ValueError("text must be a non-empty string")
        token = os.getenv("TELEGRAM_BOT_TOKEN")
        chat_id = os.getenv("TELEGRAM_CHAT_ID")
        if not token or not chat_id:
            raise RuntimeError("Missing TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID env var")
        response = _post(token, chat_id, text, "Markdown")
        if response.status_code == 400:
            # Telegram rejects Markdown it cannot parse (e.g. a URL with "_" in it).
            # Retry once as plain text instead of failing the whole send.
            response = _post(token, chat_id, text, None)
        response.raise_for_status()
        try:
            message_id = (response.json().get("result") or {}).get("message_id")
        except Exception:
            message_id = None
        return {"tool": "send_telegram", "status": "sent", "message_id": message_id}
    except Exception as exc:
        return err("send_telegram", exc)
