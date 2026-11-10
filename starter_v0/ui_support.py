"""CP5 session state around the team's existing chat.py tool loop."""
from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any
from uuid import uuid4

from chat import now_iso, run_model_tool_loop, trim_history, write_transcript
from tools import load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version

ROOT = Path(__file__).resolve().parent
PROMPT = ROOT / "artifacts/system_prompt.md"
TOOLS = ROOT / "artifacts/tools.yaml"


def redact(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: "[REDACTED]" if any(word in key.lower() for word in ("api_key", "token", "password", "access_code"))
            else redact(item) for key, item in value.items()
        }
    if isinstance(value, list):
        return [redact(item) for item in value]
    if isinstance(value, str):
        for key, secret in os.environ.items():
            if len(secret) >= 8 and any(word in key.upper() for word in ("API_KEY", "TOKEN", "PASSWORD", "ACCESS_CODE")):
                value = value.replace(secret, "[REDACTED]")
        return re.sub(r"sk-[A-Za-z0-9_-]{8,}", "[REDACTED]", value)
    return value


def new_session() -> dict[str, Any]:
    return {
        "transcript_id": f"cp5-team-ui_{uuid4().hex}",
        **artifact_version_dict(build_artifact_version("cp5-team", PROMPT, TOOLS)),
        "provider": "openai", "model": "gpt-4o-mini",
        "system_prompt": "artifacts/system_prompt.md", "tools": "artifacts/tools.yaml",
        "history_window": 5, "max_tool_rounds": 4,
        "created_at": now_iso(), "updated_at": now_iso(), "turns": [],
    }


def run_turn(session: dict[str, Any], text: str, provider: Any, *, directory: Path | None = None) -> None:
    if not isinstance(text, str) or not text.strip() or len(text) > 6000:
        raise ValueError("Nhập từ 1 đến 6000 ký tự.")
    if len(session["turns"]) >= 20:
        raise ValueError("Phiên đã đủ 20 lượt. Hãy tạo cuộc trò chuyện mới.")
    current = build_artifact_version("cp5-team", PROMPT, TOOLS)
    if current.prompt_hash != session["prompt_hash"] or current.tools_hash != session["tools_hash"]:
        raise ValueError("Cấu hình agent đã đổi. Hãy tạo cuộc trò chuyện mới.")
    history = []
    for turn in session["turns"]:
        if turn["status"] != "provider_error":
            history.extend([
                {"role": "user", "content": turn["user"]},
                {"role": "assistant", "content": turn["assistant_text"]},
            ])
    record = {
        "turn_index": len(session["turns"]) + 1, "user": text,
        "started_at": now_iso(), "assistant_text": "", "rounds": [], "tool_events": [],
    }
    try:
        record.update(run_model_tool_loop(
            provider=provider,
            messages=[{"role": "system", "content": PROMPT.read_text(encoding="utf-8")},
                      *trim_history(history, 5), {"role": "user", "content": text}],
            tools=to_openai_tools(load_tool_declarations(TOOLS)),
            model=session["model"], max_tool_rounds=4,
        ))
    except Exception as exc:
        record.update(status="provider_error", error=f"{type(exc).__name__}: {exc}")
    record["ended_at"] = now_iso()
    session["turns"].append(redact(record))
    write_transcript((directory or ROOT / "transcripts") / f"{session['transcript_id']}.transcript.json", redact(session))


def transcript_json(session: dict[str, Any]) -> str:
    return json.dumps(redact(session), ensure_ascii=False, indent=2)
