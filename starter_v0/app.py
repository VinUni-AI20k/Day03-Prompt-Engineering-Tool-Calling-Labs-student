"""Streamlit UI for the Research Agent.

Run from starter_v0/:

    streamlit run app.py

Reuses the same tool loop and transcript format as chat.py, so every UI turn is
logged to transcripts/*.transcript.json and counts as live-chat evidence.
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import streamlit as st

from chat import (
    ARTIFACTS_DIR,
    ROOT,
    now_iso,
    run_model_tool_loop,
    safe_slug,
    trim_history,
    write_transcript,
)
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version


PROVIDERS = ["openrouter", "openai", "anthropic", "gemini", "ollama"]
TRANSCRIPTS_DIR = ROOT / "transcripts"
SAMPLE_QUESTIONS = [
    "Tìm tin tức mới nhất về OpenAI trong tuần này",
    "Xem bài đăng gần đây của tài khoản này giúp mình",
    "Đọc và tóm tắt bài viết này: https://www.anthropic.com/news",
    "Tổng hợp tin AI hôm nay thành digest rồi gửi lên Telegram",
    "Chính sách công ty về trích dẫn nguồn quy định gì?",
]


st.set_page_config(page_title="Research Agent", page_icon="🔎", layout="wide")


# ---------- helpers ----------

def artifact_files(suffixes: tuple[str, ...]) -> list[Path]:
    return sorted(p for p in ARTIFACTS_DIR.iterdir() if p.suffix in suffixes)


def new_transcript(cfg: dict[str, Any], artifact_version: Any, model: str | None) -> tuple[dict[str, Any], Path]:
    timestamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
    transcript_id = "_".join([safe_slug(cfg["version"]), safe_slug(cfg["provider"]), "ui", timestamp])
    transcript = {
        "transcript_id": transcript_id,
        **artifact_version_dict(artifact_version),
        "provider": cfg["provider"],
        "model": model,
        "source": "streamlit",
        "system_prompt": str(cfg["system_prompt"]),
        "tools": str(cfg["tools"]),
        "history_window": cfg["history_window"],
        "max_tool_rounds": cfg["max_tool_rounds"],
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "turns": [],
    }
    return transcript, TRANSCRIPTS_DIR / f"{transcript_id}.transcript.json"


def reset_session(session_key: str, notice: str | None = None) -> None:
    st.session_state.session_key = session_key
    st.session_state.chat = []      # display messages: {role, content, rounds?, status?}
    st.session_state.history = []   # model context: user/assistant pairs, same as chat.py
    st.session_state.transcript = None
    st.session_state.transcript_path = None
    st.session_state.notice = notice


def queue_input(text: str) -> None:
    st.session_state.pending = text


def clarify_options(rounds: list[dict[str, Any]]) -> list[str]:
    for rnd in reversed(rounds):
        for event in rnd.get("tool_results", []):
            result = event.get("result")
            if isinstance(result, dict) and result.get("awaiting_user"):
                return [str(o) for o in result.get("options") or []]
    return []


def render_rounds(rounds: list[dict[str, Any]]) -> None:
    calls = sum(len(r.get("tool_calls", [])) for r in rounds)
    if not calls:
        return
    with st.expander(f"🔧 {calls} tool call · {len(rounds)} round", expanded=False):
        for rnd in rounds:
            st.markdown(f"**Round {rnd['round']}**")
            if rnd.get("assistant_text"):
                st.caption(rnd["assistant_text"])
            for event in rnd.get("tool_results", []):
                result = event.get("result")
                badge = ""
                if isinstance(result, dict):
                    if result.get("error"):
                        badge = " ❌"
                    elif result.get("status") == "needs_confirmation":
                        badge = " ⚠️ cần xác nhận"
                    elif result.get("awaiting_user"):
                        badge = " ❓ hỏi lại"
                st.markdown(f"`{event['tool']}`{badge}")
                st.code(json.dumps(event.get("args", {}), ensure_ascii=False, indent=2), language="json")
                if isinstance(result, dict) and result.get("markdown"):
                    st.markdown("Preview digest:")
                    st.markdown(result["markdown"])
                st.json(result, expanded=False)


def render_message(msg: dict[str, Any]) -> None:
    with st.chat_message(msg["role"], avatar="🧑" if msg["role"] == "user" else "🔎"):
        if msg.get("status") == "provider_error":
            st.error(msg["content"])
        else:
            if msg.get("status") == "waiting_for_user":
                st.caption("❓ Agent cần thêm thông tin")
            elif msg.get("status") == "max_tool_rounds":
                st.caption("⏹️ Dừng vì chạm giới hạn tool round")
            st.markdown(msg["content"])
        if msg.get("rounds"):
            render_rounds(msg["rounds"])


# ---------- sidebar: config ----------

with st.sidebar:
    st.header("⚙️ Cấu hình")
    provider_name = st.selectbox("Provider", PROVIDERS, index=0)
    model_input = st.text_input("Model (để trống = mặc định)", value="").strip() or None
    version = st.text_input("Version label", value="v3").strip() or "v0"

    prompt_files = artifact_files((".md",))
    prompt_files = [p for p in prompt_files if p.name != "REPORT.md"]
    tools_files = artifact_files((".yaml", ".yml"))
    default_prompt = ARTIFACTS_DIR / "system_prompt.md"
    default_tools = ARTIFACTS_DIR / "tools.yaml"
    system_prompt_path = st.selectbox(
        "System prompt",
        prompt_files,
        index=prompt_files.index(default_prompt) if default_prompt in prompt_files else 0,
        format_func=lambda p: p.name,
    )
    tools_path = st.selectbox(
        "Tool declarations",
        tools_files,
        index=tools_files.index(default_tools) if default_tools in tools_files else 0,
        format_func=lambda p: p.name,
    )
    history_window = st.slider("History window (cặp user/assistant)", 0, 10, 5)
    max_tool_rounds = st.slider("Max tool rounds", 1, 8, 4)

cfg = {
    "provider": provider_name,
    "model": model_input,
    "version": version,
    "system_prompt": system_prompt_path,
    "tools": tools_path,
    "history_window": history_window,
    "max_tool_rounds": max_tool_rounds,
}

# Load artifacts every rerun so edits to system_prompt.md / tools.yaml are picked up.
load_error: str | None = None
try:
    system_prompt = system_prompt_path.read_text(encoding="utf-8")
    tool_declarations = load_tool_declarations(tools_path)
    openai_tools = to_openai_tools(tool_declarations)
    artifact_version = build_artifact_version(version, system_prompt_path, tools_path)
except Exception as exc:
    load_error = f"{type(exc).__name__}: {exc}"
    system_prompt, tool_declarations, openai_tools, artifact_version = "", [], [], None

if "provider_obj" not in st.session_state or st.session_state.get("provider_name") != provider_name:
    st.session_state.provider_obj = make_provider(provider_name)
    st.session_state.provider_name = provider_name
provider = st.session_state.provider_obj
selected_model = model_input or getattr(provider, "default_model", None)

# One transcript per (provider, model, artifact_version) — same rule as chat.py,
# so a run's prompt/tool hashes always match what the model actually saw.
session_key = "|".join([
    provider_name,
    selected_model or "",
    artifact_version.artifact_version if artifact_version else "invalid",
])
if "session_key" not in st.session_state:
    reset_session(session_key)
elif st.session_state.session_key != session_key:
    had_chat = bool(st.session_state.chat)
    reset_session(session_key, "Cấu hình hoặc prompt/tools đã đổi → bắt đầu transcript mới." if had_chat else None)

with st.sidebar:
    if artifact_version:
        st.caption(f"`{artifact_version.artifact_version}`")
    st.caption(f"Model: `{selected_model}`")
    if st.button("🗑️ Chat mới", width="stretch"):
        reset_session(session_key)
        st.rerun()

    if st.session_state.transcript_path:
        path: Path = st.session_state.transcript_path
        st.caption(f"Transcript: `{path.relative_to(ROOT)}`")
        st.download_button(
            "⬇️ Tải transcript JSON",
            data=json.dumps(st.session_state.transcript, ensure_ascii=False, indent=2, default=str),
            file_name=path.name,
            mime="application/json",
            width="stretch",
        )

    st.divider()
    st.subheader(f"🧰 Tools ({len(tool_declarations)})")
    for decl in tool_declarations:
        with st.expander(decl["name"]):
            st.write(decl.get("description") or "_(chưa có description)_")
            params = (decl.get("parameters") or {}).get("properties") or {}
            if params:
                st.code(json.dumps(params, ensure_ascii=False, indent=2), language="json")


# ---------- main: chat ----------

st.title("🔎 Research Agent")
st.caption("Tìm tin theo từ khóa / tài khoản, đọc URL, tổng hợp digest — mọi lượt chat được log vào `transcripts/`.")

if load_error:
    st.error(f"Không load được prompt/tools: {load_error}")
    st.stop()

if st.session_state.get("notice"):
    st.info(st.session_state.notice)
    st.session_state.notice = None

if not st.session_state.chat:
    st.markdown("**Thử nhanh:**")
    cols = st.columns(len(SAMPLE_QUESTIONS))
    for col, question in zip(cols, SAMPLE_QUESTIONS):
        col.button(question, on_click=queue_input, args=(question,), width="stretch")

for msg in st.session_state.chat:
    render_message(msg)

# Quick-reply buttons when the agent called clarify with options.
last = st.session_state.chat[-1] if st.session_state.chat else None
if last and last.get("status") == "waiting_for_user":
    options = clarify_options(last.get("rounds", []))
    if options:
        cols = st.columns(len(options))
        for i, (col, option) in enumerate(zip(cols, options)):
            col.button(option, key=f"opt_{len(st.session_state.chat)}_{i}", on_click=queue_input, args=(option,))

typed = st.chat_input("Hỏi agent…")
user_text = (typed or st.session_state.pop("pending", None) or "").strip()

if user_text:
    if st.session_state.transcript is None:
        st.session_state.transcript, st.session_state.transcript_path = new_transcript(cfg, artifact_version, selected_model)
    transcript = st.session_state.transcript
    transcript["history_window"] = history_window
    transcript["max_tool_rounds"] = max_tool_rounds

    user_msg = {"role": "user", "content": user_text}
    st.session_state.chat.append(user_msg)
    render_message(user_msg)

    messages = [
        {"role": "system", "content": system_prompt},
        *trim_history(st.session_state.history, history_window),
        {"role": "user", "content": user_text},
    ]
    turn_record: dict[str, Any] = {
        "turn_index": len(transcript["turns"]) + 1,
        "started_at": now_iso(),
        "user": user_text,
        "status": "started",
        "assistant_text": None,
        "rounds": [],
        "tool_events": [],
    }

    with st.chat_message("assistant", avatar="🔎"):
        with st.spinner("Agent đang suy nghĩ và gọi tool…"):
            try:
                result = run_model_tool_loop(
                    provider=provider,
                    messages=messages,
                    tools=openai_tools,
                    model=model_input,
                    max_tool_rounds=max_tool_rounds,
                )
                turn_record.update(result)
                st.session_state.history.append({"role": "user", "content": user_text})
                st.session_state.history.append({"role": "assistant", "content": result["assistant_text"]})
                assistant_msg = {
                    "role": "assistant",
                    "content": result["assistant_text"] or "_(không có nội dung)_",
                    "rounds": result["rounds"],
                    "status": result["status"],
                }
            except Exception as exc:
                error = f"{type(exc).__name__}: {exc}"
                turn_record.update({"status": "provider_error", "error": error})
                assistant_msg = {"role": "assistant", "content": error, "status": "provider_error"}

    turn_record["ended_at"] = now_iso()
    transcript["turns"].append(turn_record)
    write_transcript(st.session_state.transcript_path, transcript)

    st.session_state.chat.append(assistant_msg)
    st.rerun()
