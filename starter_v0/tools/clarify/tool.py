from __future__ import annotations

from typing import Any


def ask_user(question: str = "", response_type: str = "text", options: list[str] | None = None) -> dict[str, Any]:
    if response_type == "choice" and not options:
        return {
            "tool": "ask_user",
            "error": "ValueError",
            "message": "response_type='choice' requires a non-empty options list",
        }
    return {
        "tool": "ask_user",
        "question": question,
        "response_type": response_type,
        "options": options or [],
        "awaiting_user": True,
    }
