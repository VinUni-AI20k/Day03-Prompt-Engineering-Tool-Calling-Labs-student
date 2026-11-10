"""Web UI backend for the Research Agent (CP5).

Reuses the exact agent loop of chat.py (run_model_tool_loop + write_transcript),
so the web UI behaves like the CLI and writes transcripts in the same format.

Run (from starter_v0/ui):
    ..\\.venv\\Scripts\\python -m uvicorn server:app --port 8000

Env (optional):
    UI_PROVIDER          gemini | openrouter | openai | anthropic | ollama   (default: gemini)
    UI_MODEL             model override                                        (default: provider default)
    UI_VERSION           artifact version label written to transcripts       (default: v4)
    UI_MAX_TURNS         max user turns per browser session                   (default: 15)
    UI_TRANSCRIPTS_DIR   where transcripts go                                  (default: starter_v0/transcripts)
"""
from __future__ import annotations

import os
import sys
import threading
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

# Windows consoles default to cp1252; chat.py prints emoji for every tool call.
for stream in (sys.stdout, sys.stderr):
    try:
        stream.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

UI_DIR = Path(__file__).resolve().parent
ROOT = UI_DIR.parent
sys.path.insert(0, str(ROOT))

from fastapi import FastAPI, HTTPException  # noqa: E402
from fastapi.responses import FileResponse, JSONResponse  # noqa: E402
from fastapi.staticfiles import StaticFiles  # noqa: E402
from pydantic import BaseModel, Field  # noqa: E402

from chat import (  # noqa: E402  (importing chat also loads starter_v0/.env)
    ARTIFACTS_DIR,
    now_iso,
    run_model_tool_loop,
    safe_slug,
    trim_history,
    write_transcript,
)
from providers import make_provider  # noqa: E402
from tools import load_tool_declarations, to_openai_tools  # noqa: E402
from versioning import artifact_version_dict, build_artifact_version  # noqa: E402

PROVIDER_NAME = os.getenv("UI_PROVIDER", "gemini")
MODEL = os.getenv("UI_MODEL") or None
VERSION = os.getenv("UI_VERSION", "v4")
MAX_TURNS = int(os.getenv("UI_MAX_TURNS", "15"))
TRANSCRIPTS_DIR = Path(os.getenv("UI_TRANSCRIPTS_DIR") or ROOT / "transcripts")
HISTORY_WINDOW = 5      # same defaults as chat.py
MAX_TOOL_ROUNDS = 4
MAX_MESSAGE_CHARS = 2000
MAX_SESSIONS = 200

SYSTEM_PROMPT_PATH = ARTIFACTS_DIR / "system_prompt.md"
TOOLS_PATH = ARTIFACTS_DIR / "tools.yaml"
SYSTEM_PROMPT = SYSTEM_PROMPT_PATH.read_text(encoding="utf-8")
TOOL_DECLARATIONS = load_tool_declarations(TOOLS_PATH)
OPENAI_TOOLS = to_openai_tools(TOOL_DECLARATIONS)
ARTIFACT_VERSION = build_artifact_version(VERSION, SYSTEM_PROMPT_PATH, TOOLS_PATH)
PROVIDER = make_provider(PROVIDER_NAME)
SELECTED_MODEL = MODEL or getattr(PROVIDER, "default_model", None)

# Env keys each tool needs at run time (the model only needs the provider key).
# Tools whose keys are missing still get called by the model, but return an error dict —
# the UI marks them so testers know the error is configuration, not routing.
TOOL_REQUIRED_ENV = {
    "lookup": ["TAVILY_API_KEY"],
    "fetch": ["FIRECRAWL_API_KEY"],
    "timeline": ["RAPIDAPI_KEY"],
    "social_search": ["RAPIDAPI_KEY"],
    "send": ["TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID"],
}

SAMPLE_QUESTIONS = [
    "Tin tức AI hôm nay có gì nổi bật?",
    "Transformer trong deep learning là gì?",
    "Tóm tắt bài viết này hộ mình",
    "Tóm tắt bài này giúp mình: https://openai.com/research/",
    "Tìm paper arXiv mới về AI agent evaluation",
    "Theo policy công ty, đăng bản tin lên Telegram có cần xác nhận trước không?",
    "Đăng bản tin AI hôm nay lên Telegram giúp mình",
]


def _missing_env(tool_name: str) -> list[str]:
    return [name for name in TOOL_REQUIRED_ENV.get(tool_name, []) if not os.getenv(name)]


class Session:
    def __init__(self, session_id: str) -> None:
        self.lock = threading.Lock()
        self.history: list[dict[str, str]] = []
        timestamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
        self.transcript_id = "_".join(["ui", safe_slug(VERSION), safe_slug(PROVIDER_NAME), timestamp])
        self.path = TRANSCRIPTS_DIR / f"{self.transcript_id}.transcript.json"
        self.transcript: dict[str, Any] = {
            "transcript_id": self.transcript_id,
            "interface": "web_ui",
            "session_id": session_id,
            **artifact_version_dict(ARTIFACT_VERSION),
            "provider": PROVIDER_NAME,
            "model": SELECTED_MODEL,
            "system_prompt": str(SYSTEM_PROMPT_PATH.relative_to(ROOT)),
            "tools": str(TOOLS_PATH.relative_to(ROOT)),
            "history_window": HISTORY_WINDOW,
            "max_tool_rounds": MAX_TOOL_ROUNDS,
            "created_at": now_iso(),
            "updated_at": now_iso(),
            "turns": [],
        }

    @property
    def turn_count(self) -> int:
        return len(self.transcript["turns"])


_sessions: dict[str, Session] = {}
_sessions_lock = threading.Lock()


def get_session(session_id: str, *, create: bool = True) -> Session | None:
    with _sessions_lock:
        session = _sessions.get(session_id)
        if session is None and create:
            if len(_sessions) >= MAX_SESSIONS:
                _sessions.pop(next(iter(_sessions)))  # drop the oldest in-memory session (its transcript is on disk)
            session = _sessions[session_id] = Session(session_id)
        return session


class ChatRequest(BaseModel):
    session_id: str = Field(min_length=8, max_length=64)
    message: str = Field(min_length=1, max_length=MAX_MESSAGE_CHARS)


class ResetRequest(BaseModel):
    session_id: str = Field(min_length=8, max_length=64)


app = FastAPI(title="Research Agent UI", docs_url=None, redoc_url=None)


def _first_sentence(text: str) -> str:
    text = " ".join((text or "").split())
    for sep in (". ", "; "):
        if sep in text:
            return text.split(sep, 1)[0].rstrip(".") + "."
    return text


@app.get("/api/info")
def info() -> dict[str, Any]:
    return {
        "provider": PROVIDER_NAME,
        "model": SELECTED_MODEL,
        "version": VERSION,
        "artifact_version": ARTIFACT_VERSION.artifact_version,
        "max_turns": MAX_TURNS,
        "telegram_configured": bool(os.getenv("TELEGRAM_BOT_TOKEN") and os.getenv("TELEGRAM_CHAT_ID")),
        "tools": [{
            "name": t["name"],
            "summary": _first_sentence(t.get("description", "")),
            "missing_env": _missing_env(t["name"]),
        } for t in TOOL_DECLARATIONS],
        "sample_questions": SAMPLE_QUESTIONS,
    }


@app.post("/api/chat")
def chat(request: ChatRequest) -> dict[str, Any]:
    session = get_session(request.session_id)
    assert session is not None
    if not session.lock.acquire(blocking=False):
        raise HTTPException(status_code=409, detail="Lượt trước vẫn đang chạy, đợi một chút nhé.")
    try:
        if session.turn_count >= MAX_TURNS:
            raise HTTPException(status_code=429, detail=f"Phiên này đã dùng hết {MAX_TURNS} lượt. Bấm 'Cuộc chat mới' để bắt đầu lại.")

        user_text = request.message.strip()
        if not user_text:
            raise HTTPException(status_code=400, detail="Tin nhắn rỗng.")

        turn_index = session.turn_count + 1
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            *trim_history(session.history, HISTORY_WINDOW),
            {"role": "user", "content": user_text},
        ]
        turn_record: dict[str, Any] = {
            "turn_index": turn_index,
            "started_at": now_iso(),
            "user": user_text,
            "status": "started",
            "assistant_text": None,
            "rounds": [],
            "tool_events": [],
        }
        try:
            result = run_model_tool_loop(
                provider=PROVIDER,
                messages=messages,
                tools=OPENAI_TOOLS,
                model=MODEL,
                max_tool_rounds=MAX_TOOL_ROUNDS,
            )
            turn_record.update(result)
            session.history.append({"role": "user", "content": user_text})
            session.history.append({"role": "assistant", "content": result["assistant_text"]})
        except Exception as exc:  # provider errors are shown in the UI, never hidden
            turn_record.update({"status": "provider_error", "error": f"{type(exc).__name__}: {exc}"})

        turn_record["ended_at"] = now_iso()
        session.transcript["turns"].append(turn_record)
        write_transcript(session.path, session.transcript)

        return {
            "turn_index": turn_index,
            "status": turn_record["status"],
            "assistant_text": turn_record.get("assistant_text"),
            "error": turn_record.get("error"),
            "rounds": turn_record.get("rounds", []),
            "remaining_turns": MAX_TURNS - session.turn_count,
            "transcript_id": session.transcript_id,
        }
    finally:
        session.lock.release()


@app.post("/api/reset")
def reset(request: ResetRequest) -> dict[str, Any]:
    with _sessions_lock:
        _sessions.pop(request.session_id, None)
    return {"ok": True}


# ---------------- static React build ----------------
DIST_DIR = UI_DIR / "web" / "dist"

if (DIST_DIR / "index.html").exists():
    app.mount("/assets", StaticFiles(directory=DIST_DIR / "assets"), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    def spa(full_path: str) -> FileResponse:
        candidate = (DIST_DIR / full_path).resolve()
        if full_path and candidate.is_file() and DIST_DIR in candidate.parents:
            return FileResponse(candidate)
        return FileResponse(DIST_DIR / "index.html")
else:
    @app.get("/", include_in_schema=False)
    def no_build() -> JSONResponse:
        return JSONResponse(
            {"message": "React build not found. Run: cd starter_v0/ui/web && npm install && npm run build"},
            status_code=503,
        )
