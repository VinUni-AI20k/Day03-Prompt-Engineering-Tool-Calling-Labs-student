"""Thin FastAPI wrapper around the research agent for the web UI.

Run from starter_v0/:
    python server.py --provider openai --version v2

It reuses the same agent loop as chat.py (tools, prompt, transcript format) but
streams every step (model thinking, tool call, tool result, final answer) as
Server-Sent Events so the UI can show the tool timeline live.
Binds to 127.0.0.1 only; the web app proxies /api/* to it.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import threading
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Iterator

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field

from chat import (
    ARTIFACTS_DIR,
    ROOT,
    assistant_tool_message,
    execute_tool_call,
    now_iso,
    safe_slug,
    tool_results_message,
    trim_history,
    write_transcript,
)
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version

SECRET_ENV_HINTS = ("KEY", "TOKEN", "SECRET", "PASSWORD")


class Settings:
    provider_name: str = "openai"
    model: str | None = None
    version: str = "web"
    system_prompt_path: Path = ARTIFACTS_DIR / "system_prompt.md"
    tools_path: Path = ARTIFACTS_DIR / "tools.yaml"
    transcripts_dir: Path = ROOT / "transcripts"
    history_window: int = 5
    max_tool_rounds: int = 4


settings = Settings()
_provider: Any = None
_provider_lock = threading.Lock()
sessions: dict[str, dict[str, Any]] = {}

app = FastAPI(title="Research Agent API")


# ---------------------------------------------------------------- helpers

def secret_values() -> list[str]:
    """Secret values currently in the environment, longest first, for redaction."""
    values = {
        value for name, value in os.environ.items()
        if any(hint in name.upper() for hint in SECRET_ENV_HINTS) and len(value) >= 8
    }
    return sorted(values, key=len, reverse=True)


def redact(text: str) -> str:
    for value in secret_values():
        text = text.replace(value, "[REDACTED]")
    # Telegram bot URLs: .../bot<id>:<token>/method
    return re.sub(r"bot\d{6,}:[A-Za-z0-9_-]{20,}", "bot[REDACTED]", text)


def clean(value: Any) -> Any:
    """Round-trip through JSON so secrets never reach the browser or transcripts."""
    return json.loads(redact(json.dumps(value, ensure_ascii=False, default=str)))


def get_provider() -> Any:
    global _provider
    with _provider_lock:
        if _provider is None:
            _provider = make_provider(settings.provider_name)
        return _provider


VERSIONS_DIR = ARTIFACTS_DIR / "versions"
VERSION_LABELS = {
    "v0": "Bản gốc của bài mẫu",
    "v1": "Hỏi lại và xin xác nhận",
    "v2": "Rule chọn công cụ",
    "v3": "Mô tả công cụ rõ hơn",
}


def available_versions() -> list[str]:
    """Frozen versions: artifacts/versions/<vN>/{system_prompt.md,tools.yaml}."""
    if not VERSIONS_DIR.is_dir():
        return []
    found = [
        d.name for d in VERSIONS_DIR.iterdir()
        if re.fullmatch(r"v\d+", d.name) and (d / "system_prompt.md").is_file() and (d / "tools.yaml").is_file()
    ]
    return sorted(found, key=lambda name: int(name[1:]))


def version_paths(version: str | None) -> tuple[str, Path, Path]:
    """(label, prompt path, tools path) of a frozen version; the live files when version is None."""
    if version is None:
        return settings.version, settings.system_prompt_path, settings.tools_path
    if version not in available_versions():
        raise ValueError(f"Không có version {version!r}. Có: {', '.join(available_versions()) or 'không'}")
    base = VERSIONS_DIR / version
    return version, base / "system_prompt.md", base / "tools.yaml"


def default_version() -> str | None:
    """Version the UI preselects: the one the server was started with, if it is frozen."""
    versions = available_versions()
    if settings.version in versions:
        return settings.version
    return versions[-1] if versions else None


def version_accuracy() -> dict[str, float]:
    """case_accuracy per version, read from artifacts/version_log.csv (the evidence log)."""
    log = ARTIFACTS_DIR / "version_log.csv"
    scores: dict[str, float] = {}
    if not log.is_file():
        return scores
    for row in csv.DictReader(log.open(encoding="utf-8")):
        match = re.search(r"case_accuracy=([0-9.]+)", row.get("metric_after", ""))
        if match and row.get("version"):
            scores[row["version"]] = float(match.group(1))
    return scores


def new_session(source: str = "web_ui", version: str | None = None) -> dict[str, Any]:
    label, prompt_path, tools_path = version_paths(version)
    system_prompt = prompt_path.read_text(encoding="utf-8")
    declarations = load_tool_declarations(tools_path)
    artifact = build_artifact_version(label, prompt_path, tools_path)
    provider = get_provider()
    model = settings.model or getattr(provider, "default_model", None)
    session_id = uuid.uuid4().hex[:12]
    transcript_id = "_".join([
        safe_slug(label),
        safe_slug(settings.provider_name),
        safe_slug(source.replace("_ui", "")),
        datetime.now().strftime("%Y%m%dT%H%M%S%f"),
    ])
    transcript = {
        "transcript_id": transcript_id,
        **artifact_version_dict(artifact),
        "provider": settings.provider_name,
        "model": model,
        "source": source,
        "system_prompt": str(prompt_path),
        "tools": str(tools_path),
        "history_window": settings.history_window,
        "max_tool_rounds": settings.max_tool_rounds,
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "turns": [],
    }
    session = {
        "id": session_id,
        "system_prompt": system_prompt,
        "tools": to_openai_tools(declarations),
        "history": [],
        "transcript": transcript,
        "path": settings.transcripts_dir / f"{transcript_id}.transcript.json",
        "lock": threading.Lock(),
    }
    sessions[session_id] = session
    return session


def sse(event: dict[str, Any]) -> str:
    return f"data: {json.dumps(clean(event), ensure_ascii=False)}\n\n"


def ask_from_result(call_args: dict[str, Any], result: dict[str, Any]) -> dict[str, Any]:
    return {
        "question": result.get("question") or call_args.get("question") or "Bạn bổ sung thêm thông tin nhé.",
        "response_type": result.get("response_type") or call_args.get("response_type") or "text",
        "options": result.get("options") or call_args.get("options") or [],
    }


# ---------------------------------------------------------------- streaming agent loop

def stream_turn(session: dict[str, Any], user_text: str) -> Iterator[str]:
    provider = get_provider()
    model = session["transcript"]["model"]
    messages = [
        {"role": "system", "content": session["system_prompt"]},
        *trim_history(session["history"], settings.history_window),
        {"role": "user", "content": user_text},
    ]
    turn: dict[str, Any] = {
        "turn_index": len(session["transcript"]["turns"]) + 1,
        "started_at": now_iso(),
        "user": user_text,
        "status": "started",
        "assistant_text": None,
        "rounds": [],
        "tool_events": [],
    }
    final: dict[str, Any] | None = None

    try:
        for round_index in range(1, settings.max_tool_rounds + 1):
            yield sse({"type": "thinking", "round": round_index})
            response = provider.complete(messages, session["tools"], model=model, temperature=0.0)
            calls = response.tool_calls
            record: dict[str, Any] = {
                "round": round_index,
                "assistant_text": response.text,
                "tool_calls": [{"name": c.name, "args": c.args} for c in calls],
                "tool_results": [],
            }

            if not calls:
                turn["rounds"].append(record)
                turn.update(status="answered", assistant_text=response.text or "")
                final = {"type": "final", "status": "answered", "text": response.text or ""}
                break

            if response.text:
                yield sse({"type": "note", "text": response.text})
            messages.append(assistant_tool_message(response.text, calls))
            events_for_model: list[dict[str, Any]] = []
            paused: dict[str, Any] | None = None

            for index, call in enumerate(calls):
                call_id = f"{round_index}-{index}"
                yield sse({"type": "tool_call", "id": call_id, "name": call.name, "args": call.args})
                started = time.perf_counter()
                event = execute_tool_call(call)
                duration_ms = int((time.perf_counter() - started) * 1000)
                record["tool_results"].append(event)
                turn["tool_events"].append(event)
                result = event.get("result", {})
                failed = isinstance(result, dict) and bool(result.get("error"))
                yield sse({
                    "type": "tool_result", "id": call_id, "name": call.name,
                    "result": result, "duration_ms": duration_ms, "error": failed,
                })
                if isinstance(result, dict) and result.get("awaiting_user"):
                    paused = ask_from_result(call.args, result)
                    break
                events_for_model.append(event)

            turn["rounds"].append(record)
            if paused:
                turn.update(status="waiting_for_user", assistant_text=paused["question"])
                final = {"type": "final", "status": "waiting_for_user", "text": paused["question"], "ask": paused}
                break
            messages.append(tool_results_message(events_for_model))
        else:
            text = f"Stopped after {settings.max_tool_rounds} tool rounds. Inspect the transcript for details."
            turn.update(status="max_tool_rounds", assistant_text=text)
            final = {"type": "final", "status": "max_tool_rounds", "text": text}

        session["history"].append({"role": "user", "content": user_text})
        session["history"].append({"role": "assistant", "content": turn["assistant_text"] or ""})
    except Exception as exc:  # surface provider/network errors instead of hiding them
        message = redact(f"{type(exc).__name__}: {exc}")
        turn.update(status="provider_error", error=message)
        final = {"type": "error", "message": message}

    turn["ended_at"] = now_iso()
    session["transcript"]["turns"].append(turn)
    write_transcript(session["path"], clean(session["transcript"]))
    if final:
        yield sse(final)


def turn_events(session: dict[str, Any], user_text: str) -> Iterator[dict[str, Any]]:
    """Same agent turn as stream_turn, as plain dicts (used by the Telegram bot)."""
    for frame in stream_turn(session, user_text):
        yield json.loads(frame[len("data: "):])


# ---------------------------------------------------------------- routes

class ChatRequest(BaseModel):
    session_id: str | None = None
    message: str = Field(min_length=1, max_length=4000)
    version: str | None = None  # only used when a new session starts


@app.get("/api/health")
def health() -> dict[str, Any]:
    label, prompt_path, tools_path = version_paths(default_version())
    artifact = build_artifact_version(label, prompt_path, tools_path)
    provider_ok = True
    try:
        provider = get_provider()
        model = settings.model or getattr(provider, "default_model", None)
    except Exception as exc:
        provider_ok, model = False, None
        return {"ok": False, "error": redact(f"{type(exc).__name__}: {exc}")}
    return {
        "ok": provider_ok,
        "provider": settings.provider_name,
        "model": model,
        "version": label,
        "artifact_version": artifact.artifact_version,
    }


@app.get("/api/versions")
def versions() -> dict[str, Any]:
    scores = version_accuracy()
    items = []
    for name in available_versions():
        _, prompt_path, tools_path = version_paths(name)
        items.append({
            "id": name,
            "label": VERSION_LABELS.get(name, name),
            "accuracy": scores.get(name),
            "artifact_version": build_artifact_version(name, prompt_path, tools_path).artifact_version,
        })
    return {"default": default_version(), "versions": items}


@app.get("/api/tools")
def tools(version: str | None = None) -> list[dict[str, str]]:
    try:
        _, _, tools_path = version_paths(version or default_version())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    declarations = load_tool_declarations(tools_path)
    return [{"name": d["name"], "description": d.get("description", "")} for d in declarations]


@app.post("/api/chat")
def chat(req: ChatRequest) -> StreamingResponse:
    session = sessions.get(req.session_id or "") if req.session_id else None
    if session is None:
        try:
            session = new_session(version=req.version or default_version())
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))
        except Exception as exc:
            raise HTTPException(status_code=500, detail=redact(f"{type(exc).__name__}: {exc}"))
    if not session["lock"].acquire(blocking=False):
        raise HTTPException(status_code=409, detail="Phiên này đang xử lý một yêu cầu khác.")

    def generate() -> Iterator[str]:
        try:
            yield sse({"type": "session", "session_id": session["id"]})
            yield from stream_turn(session, req.message.strip())
        finally:
            session["lock"].release()

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache, no-transform", "X-Accel-Buffering": "no"},
    )


@app.get("/api/transcript/{session_id}")
def transcript(session_id: str) -> JSONResponse:
    session = sessions.get(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy phiên.")
    filename = f"{session['transcript']['transcript_id']}.transcript.json"
    return JSONResponse(
        clean(session["transcript"]),
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@app.delete("/api/session/{session_id}")
def delete_session(session_id: str) -> dict[str, bool]:
    return {"deleted": sessions.pop(session_id, None) is not None}


# ---------------------------------------------------------------- entrypoint

def main() -> None:
    import uvicorn

    parser = argparse.ArgumentParser(description="Research Agent API for the web UI.")
    parser.add_argument("--provider", choices=["openrouter", "openai", "anthropic", "gemini", "ollama"], required=True)
    parser.add_argument("--model", default=None)
    parser.add_argument("--version", default="web", help="Artifact version label stored in transcripts, e.g. v2.")
    parser.add_argument("--system-prompt", type=Path, default=settings.system_prompt_path)
    parser.add_argument("--tools", type=Path, default=settings.tools_path)
    parser.add_argument("--transcripts-dir", type=Path, default=settings.transcripts_dir)
    parser.add_argument("--max-tool-rounds", type=int, default=settings.max_tool_rounds)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()

    settings.provider_name = args.provider
    settings.model = args.model
    settings.version = args.version
    settings.system_prompt_path = args.system_prompt
    settings.tools_path = args.tools
    settings.transcripts_dir = args.transcripts_dir
    settings.max_tool_rounds = args.max_tool_rounds
    uvicorn.run(app, host=args.host, port=args.port, log_level="info")


if __name__ == "__main__":
    main()
