"""Local Streamlit UI: chat with the agent, or run an eval suite and read the log."""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import streamlit as st

from chat import now_iso, run_model_tool_loop, safe_slug, trim_history, write_transcript
from env_loader import load_lab_env
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version

ROOT = Path(__file__).parent
ARTIFACTS_DIR = ROOT / "artifacts"
RUNS_DIR = ROOT / "runs"
TRANSCRIPTS_DIR = ROOT / "transcripts"
load_lab_env(ROOT)

PROVIDERS = ["openrouter", "openai", "anthropic", "gemini", "ollama"]

st.set_page_config(page_title="Research Agent", page_icon="🔎", layout="wide")

for key, default in [("messages", []), ("history", []), ("transcript", None)]:
    if key not in st.session_state:
        st.session_state[key] = default


def render_events(events: list[dict]) -> None:
    for event in events:
        with st.expander(f"🔧 {event.get('tool')} {json.dumps(event.get('args', {}), ensure_ascii=False)}"):
            st.json(event.get("result"), expanded=False)


def render_turn(message: dict) -> None:
    with st.chat_message(message["role"]):
        st.markdown(message["content"] or "_(không có nội dung text)_")
        render_events(message.get("events") or [])


def get_transcript(provider_name: str, model: str, version: str, prompt_path: str, tools_path: str) -> dict:
    if st.session_state.transcript is None:
        artifact_version = build_artifact_version(version, Path(prompt_path), Path(tools_path))
        timestamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
        st.session_state.transcript = {
            "transcript_id": "_".join([safe_slug(version), safe_slug(provider_name), timestamp]),
            **artifact_version_dict(artifact_version),
            "provider": provider_name,
            "model": model or getattr(make_provider(provider_name), "default_model", None),
            "system_prompt": prompt_path,
            "tools": tools_path,
            "history_window": int(st.session_state.history_window),
            "max_tool_rounds": int(st.session_state.max_tool_rounds),
            "created_at": now_iso(),
            "updated_at": now_iso(),
            "turns": [],
        }
    return st.session_state.transcript


# ---------------- sidebar ----------------
with st.sidebar:
    st.header("Cấu hình")
    mode = st.radio("Chế độ", ["Chat", "Eval"], horizontal=True)
    provider_name = st.selectbox("Provider", PROVIDERS, index=0)
    model = st.text_input("Model (trống = mặc định)")
    version = st.text_input("Version label", value="v1")
    prompt_path = st.text_input("System prompt", value=str(ARTIFACTS_DIR / "system_prompt.md"))
    tools_path = st.text_input("Tools yaml", value=str(ARTIFACTS_DIR / "tools.yaml"))
    st.session_state.max_tool_rounds = st.number_input("Max tool rounds", 1, 10, 4)
    st.session_state.history_window = st.number_input("History window", 0, 20, 5)

    if st.button("Phiên mới"):
        st.session_state.messages = []
        st.session_state.history = []
        st.session_state.transcript = None
        st.rerun()

    st.caption("Agent chạy thật trên máy bạn, tốn credit API của bạn.")

if mode == "Chat":
    for message in st.session_state.messages:
        render_turn(message)

    user_text = st.chat_input("Nhập câu hỏi...")
    if user_text:
        st.session_state.messages.append({"role": "user", "content": user_text})
        render_turn({"role": "user", "content": user_text})

        system_prompt = Path(prompt_path).read_text(encoding="utf-8")
        openai_tools = to_openai_tools(load_tool_declarations(Path(tools_path)))
        messages = [
            {"role": "system", "content": system_prompt},
            *trim_history(st.session_state.history, int(st.session_state.history_window)),
            {"role": "user", "content": user_text},
        ]

        with st.chat_message("assistant"):
            with st.spinner("Đang chạy agent..."):
                try:
                    result = run_model_tool_loop(
                        provider=make_provider(provider_name),
                        messages=messages,
                        tools=openai_tools,
                        model=model or None,
                        max_tool_rounds=int(st.session_state.max_tool_rounds),
                    )
                    status, answer = result["status"], result["assistant_text"]
                except Exception as exc:
                    status, answer = "provider_error", f"{type(exc).__name__}: {exc}"
                st.markdown(answer)
                render_events(result.get("tool_events", []) if status != "provider_error" else [])

        st.session_state.messages.append(
            {"role": "assistant", "content": answer, "events": result.get("tool_events", []) if status != "provider_error" else []}
        )
        st.session_state.history += [{"role": "user", "content": user_text}, {"role": "assistant", "content": answer}]

        transcript = get_transcript(provider_name, model, version, prompt_path, tools_path)
        transcript["turns"].append(
            {
                "turn_index": len(transcript["turns"]) + 1,
                "started_at": now_iso(),
                "user": user_text,
                "status": status,
                "assistant_text": answer,
                "rounds": result.get("rounds", []) if status != "provider_error" else [],
                "tool_events": result.get("tool_events", []) if status != "provider_error" else [],
                "ended_at": now_iso(),
            }
        )
        write_transcript(TRANSCRIPTS_DIR / f"{transcript['transcript_id']}.transcript.json", transcript)
        st.caption(f"Transcript: transcripts/{transcript['transcript_id']}.transcript.json")

else:
    suite = st.selectbox("Suite", ["base", "group", "extension", "cross"])
    cases_path = st.text_input("Eval cases", value=str(ROOT / "data" / "eval_base.json"))

    if st.button("Chạy eval", type="primary"):
        command = [
            sys.executable, "run_eval.py",
            "--provider", provider_name,
            "--version", version,
            "--suite", suite,
            "--eval-cases", cases_path,
        ]
        if model:
            command += ["--model", model]

        with st.spinner("Đang chạy eval (có thể mất vài phút)..."):
            process = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")

        st.code((process.stdout or "") + (f"\n[stderr]\n{process.stderr}" if process.stderr.strip() else ""), language="text")

        run_files = sorted(RUNS_DIR.glob("*.json"), key=lambda path: path.stat().st_mtime)
        if run_files:
            run = json.loads(run_files[-1].read_text(encoding="utf-8"))
            st.caption(f"Run file: runs/{run_files[-1].name}")
            st.json(run.get("summary"), expanded=True)
            st.dataframe(
                [
                    {
                        "case": item["id"],
                        "passed": item["result"]["passed"],
                        "failure": item["result"].get("failure_type"),
                        "mismatch": item["result"].get("observed_mismatch"),
                        "actual_tool_calls": json.dumps(item["result"]["actual_tool_calls"], ensure_ascii=False),
                    }
                    for item in run.get("results", [])
                ],
                use_container_width=True,
            )
