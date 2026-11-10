"""HTTP chat UI — DNH team research agent.

Static Gemini-like box + POST /api/chat → cùng vòng tool loop như chat.py.
Chạy từ starter_v0:  python -m ui --provider openrouter --version v3
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import threading
import uuid
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from chat import (  # noqa: E402
    artifact_version_dict,
    now_iso,
    run_model_tool_loop,
    safe_slug,
    trim_history,
    write_transcript,
)
from env_loader import load_lab_env  # noqa: E402
from providers import make_provider  # noqa: E402
from tools import load_tool_declarations, to_openai_tools  # noqa: E402
from versioning import build_artifact_version  # noqa: E402

load_lab_env(ROOT)

STATIC = Path(__file__).resolve().parent / "static"
FILES = {
    "/": "index.html",
    "/index.html": "index.html",
    "/styles.css": "styles.css",
    "/app.js": "app.js",
}
TYPES = {
    ".html": "text/html; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".js": "text/javascript; charset=utf-8",
}
MAX_BODY = 32_000
SESSION_RE = re.compile(r"^[A-Za-z0-9_-]{8,64}$")

# Curated OpenRouter ids — đủ chọn trên UI, không cần tải cả catalog.
OPENROUTER_MODELS = [
    "openai/gpt-4o-mini",
    "openai/gpt-4o",
    "openai/gpt-4.1-mini",
    "anthropic/claude-3.5-sonnet",
    "anthropic/claude-haiku-4.5",
    "google/gemini-2.0-flash-001",
    "google/gemini-2.5-flash-preview",
    "deepseek/deepseek-chat",
    "meta-llama/llama-3.3-70b-instruct",
    "qwen/qwen-2.5-72b-instruct",
]

_CONFIG: dict[str, Any] = {}
_SESSIONS: dict[str, dict[str, Any]] = {}
_SESSIONS_LOCK = threading.Lock()


def _model_choices(session: dict[str, Any] | None = None) -> list[str]:
    provider = _CONFIG.get("provider_name")
    current = (session or {}).get("model") or _CONFIG.get("model")
    if provider == "openrouter":
        models = list(OPENROUTER_MODELS)
    else:
        models = [current] if current else []
    if current and current not in models:
        models.insert(0, current)
    return [m for m in models if m]


def _new_transcript_shell(session_id: str, model: str | None) -> tuple[dict[str, Any], Path]:
    timestamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
    transcript_id = "_".join(
        [
            safe_slug(str(_CONFIG["version"])),
            safe_slug(str(_CONFIG["provider_name"])),
            "ui",
            safe_slug(session_id[:12]),
            timestamp,
        ]
    )
    transcript_path = _CONFIG["transcripts_dir"] / f"{transcript_id}.transcript.json"
    transcript: dict[str, Any] = {
        "transcript_id": transcript_id,
        **artifact_version_dict(_CONFIG["artifact_version"]),
        "provider": _CONFIG["provider_name"],
        "model": model or _CONFIG.get("model"),
        "system_prompt": str(_CONFIG["system_path"]),
        "tools": str(_CONFIG["tools_path"]),
        "history_window": _CONFIG["history_window"],
        "max_tool_rounds": _CONFIG["max_tool_rounds"],
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "ui": "dnh-team-chat",
        "session_id": session_id,
        "turns": [],
    }
    return transcript, transcript_path


def _create_session(session_id: str) -> dict[str, Any]:
    model = _CONFIG.get("model_arg") or _CONFIG.get("model")
    transcript, transcript_path = _new_transcript_shell(session_id, model)
    return {
        "session_id": session_id,
        "history": [],
        "model": model,
        "model_arg": _CONFIG.get("model_arg") or model,
        "transcript": transcript,
        "transcript_path": transcript_path,
        "transcript_written": False,
        "lock": threading.Lock(),
    }


def get_session(session_id: str) -> dict[str, Any]:
    if not SESSION_RE.match(session_id):
        raise ValueError("session_id không hợp lệ.")
    with _SESSIONS_LOCK:
        session = _SESSIONS.get(session_id)
        if session is None:
            session = _create_session(session_id)
            _SESSIONS[session_id] = session
        return session


def reset_session(session_id: str) -> dict:
    with _SESSIONS_LOCK:
        if not SESSION_RE.match(session_id):
            raise ValueError("session_id không hợp lệ.")
        session = _create_session(session_id)
        _SESSIONS[session_id] = session
    return {
        "ok": True,
        "session_id": session_id,
        "transcript": str(session["transcript_path"]),
        "message": "Đã xóa lịch sử server; transcript mới sẽ ghi khi gửi tin đầu.",
    }


def health(session: dict[str, Any] | None = None) -> dict:
    return {
        "ok": True,
        "brand": "DNH team",
        "provider": _CONFIG.get("provider_name"),
        "model": (session or {}).get("model") or _CONFIG.get("model"),
        "models": _model_choices(session),
        "model_selectable": _CONFIG.get("provider_name") == "openrouter",
        "version": _CONFIG.get("version"),
        "session_id": (session or {}).get("session_id"),
        "transcript": str((session or {}).get("transcript_path") or ""),
    }


def set_model(session: dict[str, Any], model: str, *, require_selectable: bool = False) -> dict:
    model = (model or "").strip()
    if not model:
        raise ValueError("Thiếu model.")
    if require_selectable and _CONFIG.get("provider_name") != "openrouter":
        raise ValueError("Chỉ chọn model trên UI khi provider=openrouter.")
    session["model"] = model
    session["model_arg"] = model
    transcript = session.get("transcript")
    if isinstance(transcript, dict):
        transcript["model"] = model
        if session.get("transcript_written"):
            write_transcript(session["transcript_path"], transcript)
    return {"ok": True, "model": model, "session_id": session["session_id"]}


def execute_turn(session: dict[str, Any], user_text: str, model: str | None = None) -> dict:
    history: list[dict[str, str]] = session["history"]
    system_prompt: str = _CONFIG["system_prompt"]
    window: int = _CONFIG["history_window"]
    messages = [
        {"role": "system", "content": system_prompt},
        *trim_history(history, window),
        {"role": "user", "content": user_text},
    ]

    chosen = (model or "").strip() or session.get("model_arg") or session.get("model")
    if chosen and chosen != session.get("model"):
        set_model(session, chosen)

    turn_index = len(session["transcript"]["turns"]) + 1
    turn_record: dict[str, Any] = {
        "turn_index": turn_index,
        "started_at": now_iso(),
        "user": user_text,
        "model": chosen,
        "status": "started",
        "assistant_text": None,
        "rounds": [],
        "tool_events": [],
    }

    result = run_model_tool_loop(
        provider=_CONFIG["provider"],
        messages=messages,
        tools=_CONFIG["openai_tools"],
        model=chosen,
        max_tool_rounds=_CONFIG["max_tool_rounds"],
    )
    turn_record.update(result)
    assistant_text = str(result.get("assistant_text") or "")
    history.append({"role": "user", "content": user_text})
    history.append({"role": "assistant", "content": assistant_text})

    turn_record["ended_at"] = now_iso()
    session["transcript"]["turns"].append(turn_record)
    write_transcript(session["transcript_path"], session["transcript"])
    session["transcript_written"] = True

    tools_used = [e.get("tool") for e in result.get("tool_events") or [] if e.get("tool")]
    summary = (
        f"model={chosen} · status={result.get('status')} · "
        f"tools={', '.join(tools_used) or 'none'} · "
        f"transcript={session['transcript_path'].name}"
    )
    return {
        "ok": bool(assistant_text),
        "user_text": user_text,
        "assistant_text": assistant_text,
        "summary": summary,
        "status": result.get("status"),
        "model": chosen,
        "session_id": session["session_id"],
        "transcript": str(session["transcript_path"]),
    }


class Server(ThreadingHTTPServer):
    allow_reuse_address = True
    daemon_threads = True


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt: str, *args) -> None:
        print(f"ui {self.address_string()} {fmt % args}", flush=True)

    def _session_id_from_request(self, body: dict | None = None) -> str | None:
        header = (self.headers.get("X-Session-Id") or "").strip()
        if header:
            return header
        if body and body.get("session_id"):
            return str(body.get("session_id")).strip()
        return None

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path == "/api/health":
            session = None
            sid = self._session_id_from_request()
            if sid:
                try:
                    session = get_session(sid)
                except ValueError as exc:
                    self._send_json(400, {"error": str(exc)})
                    return
            self._send_json(200, health(session))
            return
        if path == "/favicon.ico":
            self.send_response(204)
            self.send_header("Content-Length", "0")
            self.end_headers()
            return
        name = FILES.get(path)
        if name is None:
            self._send_json(404, {"error": "Không thấy trang."})
            return
        data = (STATIC / name).read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", TYPES[Path(name).suffix])
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        body = self._read_json()
        if body is None:
            return

        sid = self._session_id_from_request(body)
        if not sid:
            self._send_json(400, {"error": "Thiếu session_id (header X-Session-Id)."})
            return
        try:
            session = get_session(sid)
        except ValueError as exc:
            self._send_json(400, {"error": str(exc)})
            return

        if path == "/api/reset":
            try:
                self._send_json(200, reset_session(sid))
            except ValueError as exc:
                self._send_json(400, {"error": str(exc)})
            return

        if path == "/api/model":
            try:
                self._send_json(
                    200,
                    set_model(session, str(body.get("model") or ""), require_selectable=True),
                )
            except ValueError as exc:
                self._send_json(400, {"error": str(exc)})
            except Exception as exc:
                self._send_json(502, {"error": str(exc).strip() or type(exc).__name__})
            return

        if path != "/api/chat":
            self._send_json(404, {"error": "Không thấy API."})
            return

        text = str(body.get("text") or "").strip()
        if not text:
            self._send_json(400, {"error": "Nhập một câu."})
            return
        model = str(body.get("model") or "").strip() or None
        if not session["lock"].acquire(blocking=False):
            self._send_json(429, {"error": "Đang xử lý lượt khác trên session này — đợi xong rồi gửi lại."})
            return
        try:
            payload = execute_turn(session, text, model=model)
        except Exception as exc:
            msg = str(exc).strip() or type(exc).__name__
            print(f"chat lỗi: {type(exc).__name__}: {exc}", flush=True)
            self._send_json(502, {"error": msg})
            return
        finally:
            session["lock"].release()
        print(f"[{sid[:8]}] you: {text}", flush=True)
        print(
            f"[{sid[:8]}] dnh[{payload.get('model')}]: {payload.get('assistant_text') or '(trống)'}",
            flush=True,
        )
        self._send_json(200, payload)

    def _read_json(self) -> dict | None:
        raw_len = self.headers.get("Content-Length", "0")
        try:
            n = int(raw_len)
        except ValueError:
            n = 0
        if n < 0 or n > MAX_BODY:
            self._send_json(413, {"error": "Câu quá dài."})
            return None
        raw = self.rfile.read(n) if n else b"{}"
        try:
            data = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            self._send_json(400, {"error": "JSON không đọc được."})
            return None
        if not isinstance(data, dict):
            self._send_json(400, {"error": "JSON phải là object."})
            return None
        return data

    def _send_json(self, code: int, payload: dict) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)
        self.wfile.flush()


def _bootstrap(args: argparse.Namespace) -> None:
    artifacts = ROOT / "artifacts"
    system_path = args.system_prompt or (artifacts / "system_prompt.md")
    tools_path = args.tools or (artifacts / "tools.yaml")
    system_prompt = system_path.read_text(encoding="utf-8")
    tool_declarations = load_tool_declarations(tools_path)
    openai_tools = to_openai_tools(tool_declarations)
    provider = make_provider(args.provider)
    selected_model = args.model or getattr(provider, "default_model", None)
    artifact_version = build_artifact_version(args.version, system_path, tools_path)
    transcripts_dir = args.transcripts_dir or (ROOT / "transcripts")
    transcripts_dir.mkdir(parents=True, exist_ok=True)

    _CONFIG.clear()
    _CONFIG.update(
        {
            "provider": provider,
            "provider_name": args.provider,
            "model": selected_model,
            "model_arg": args.model,
            "version": args.version,
            "system_prompt": system_prompt,
            "system_path": system_path,
            "tools_path": tools_path,
            "openai_tools": openai_tools,
            "history_window": args.history_window,
            "max_tool_rounds": args.max_tool_rounds,
            "artifact_version": artifact_version,
            "transcripts_dir": transcripts_dir,
        }
    )
    with _SESSIONS_LOCK:
        _SESSIONS.clear()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="DNH team chat UI (HTTP).")
    parser.add_argument(
        "--provider",
        choices=["openrouter", "openai", "anthropic", "gemini", "ollama"],
        required=True,
    )
    parser.add_argument("--model", default=None)
    parser.add_argument("--version", required=True, help="Artifact version, e.g. v3")
    parser.add_argument("--system-prompt", type=Path, default=None)
    parser.add_argument("--tools", type=Path, default=None)
    parser.add_argument("--transcripts-dir", type=Path, default=None)
    parser.add_argument("--history-window", type=int, default=5)
    parser.add_argument("--max-tool-rounds", type=int, default=4)
    # 0.0.0.0 để Cloudflare Tunnel / máy khác trong LAN mở được.
    parser.add_argument("--host", default=os.getenv("UI_HOST", "0.0.0.0"))
    parser.add_argument("--port", type=int, default=int(os.getenv("UI_PORT", "8787")))
    args = parser.parse_args(argv)

    _bootstrap(args)

    try:
        httpd = Server((args.host, args.port), Handler)
    except OSError as exc:
        print(f"Không mở được {args.host}:{args.port}: {exc}", file=sys.stderr)
        return 1

    display_host = "127.0.0.1" if args.host in {"0.0.0.0", "::"} else args.host
    print(f"DNH team chat http://{display_host}:{args.port}", flush=True)
    print(f"Bind {args.host}:{args.port} · transcript ghi khi có tin nhắn đầu", flush=True)
    print(f"Session demo id (optional): {uuid.uuid4().hex[:16]}", flush=True)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nDừng.", flush=True)
    finally:
        httpd.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
