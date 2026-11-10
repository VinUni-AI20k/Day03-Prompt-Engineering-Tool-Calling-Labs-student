"""Streamlit UI for the Research Agent.

Run from `starter_v0/`:
    streamlit run app.py

Reuses the exact tool loop of `chat.py` (same prompt, tools, clarify pause) and
writes the same transcript format to `transcripts/ui_*.transcript.json`, so UI
sessions are valid live-chat evidence. Tool errors are shown, never hidden.
"""
from __future__ import annotations

import os
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
SYSTEM_PROMPT_PATH = ARTIFACTS_DIR / "system_prompt.md"
TOOLS_PATH = ARTIFACTS_DIR / "tools.yaml"
TRANSCRIPTS_DIR = ROOT / "transcripts"

EXAMPLES = [
    "Tin tức mới nhất về AI agent trong tuần này?",
    "Sam Altman gần đây đăng gì trên X?",
    "Tóm tắt giúp tôi bài viết này",
    "Gửi bản tin vừa tổng hợp lên Telegram",
]

st.set_page_config(page_title="Research Agent — NhomSNN", page_icon="🔎", layout="wide")


# ---------------------------------------------------------------- helpers
def new_transcript(provider_name: str, model: str | None, version: str, history_window: int, max_rounds: int) -> dict[str, Any]:
    artifact_version = build_artifact_version(version, SYSTEM_PROMPT_PATH, TOOLS_PATH)
    timestamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
    transcript_id = "_".join(["ui", safe_slug(version), safe_slug(provider_name), timestamp])
    return {
        "transcript_id": transcript_id,
        **artifact_version_dict(artifact_version),
        "provider": provider_name,
        "model": model,
        "system_prompt": str(SYSTEM_PROMPT_PATH),
        "tools": str(TOOLS_PATH),
        "history_window": history_window,
        "max_tool_rounds": max_rounds,
        "interface": "streamlit",
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "turns": [],
    }


def reset_session(config: tuple) -> None:
    provider_name, model, version, history_window, max_rounds = config
    st.session_state.config = config
    st.session_state.history = []
    st.session_state.transcript = new_transcript(provider_name, model, version, history_window, max_rounds)
    st.session_state.transcript_path = TRANSCRIPTS_DIR / f"{st.session_state.transcript['transcript_id']}.transcript.json"


def result_has_error(result: Any) -> bool:
    return isinstance(result, dict) and bool(result.get("error"))


def render_turn_details(turn: dict[str, Any]) -> None:
    """Show every tool call, its args and its raw result. Errors are highlighted."""
    status = turn.get("status")
    if status == "provider_error":
        st.error(f"Provider error: {turn.get('error')}")
        return
    if status == "waiting_for_user":
        st.info("Agent đang chờ bạn trả lời câu hỏi trên (clarify).")
    elif status == "max_tool_rounds":
        st.warning("Agent dừng vì chạm giới hạn số vòng gọi tool.")

    events = turn.get("tool_events") or []
    if not events:
        st.caption("Không gọi tool nào trong lượt này.")
        return

    errors = [e for e in events if result_has_error(e.get("result"))]
    if errors:
        st.error(f"{len(errors)} tool call trả về lỗi: " + ", ".join(e.get("tool", "?") for e in errors))

    label = f"🔧 {len(events)} tool call: " + " → ".join(e.get("tool", "?") for e in events)
    with st.expander(label, expanded=bool(errors)):
        for i, event in enumerate(events, 1):
            icon = "❌" if result_has_error(event.get("result")) else "✅"
            st.markdown(f"**{i}. {icon} `{event.get('tool')}`**")
            st.json({"args": event.get("args")}, expanded=True)
            st.json({"result": event.get("result")}, expanded=False)


def run_turn(user_text: str) -> None:
    provider_name, model, _version, history_window, max_rounds = st.session_state.config
    transcript = st.session_state.transcript
    system_prompt = SYSTEM_PROMPT_PATH.read_text(encoding="utf-8")
    openai_tools = to_openai_tools(load_tool_declarations(TOOLS_PATH))

    messages = [
        {"role": "system", "content": system_prompt},
        *trim_history(st.session_state.history, history_window),
        {"role": "user", "content": user_text},
    ]
    turn: dict[str, Any] = {
        "turn_index": len(transcript["turns"]) + 1,
        "started_at": now_iso(),
        "user": user_text,
        "status": "started",
        "assistant_text": None,
        "rounds": [],
        "tool_events": [],
    }
    try:
        provider = make_provider(provider_name)
        result = run_model_tool_loop(
            provider=provider,
            messages=messages,
            tools=openai_tools,
            model=model,
            max_tool_rounds=max_rounds,
        )
        turn.update(result)
        st.session_state.history.append({"role": "user", "content": user_text})
        st.session_state.history.append({"role": "assistant", "content": result["assistant_text"]})
    except Exception as exc:  # show provider problems instead of hiding them
        turn.update({"status": "provider_error", "error": f"{type(exc).__name__}: {exc}"})

    turn["ended_at"] = now_iso()
    transcript["turns"].append(turn)
    write_transcript(st.session_state.transcript_path, transcript)


# ---------------------------------------------------------------- sidebar
with st.sidebar:
    st.header("⚙️ Cấu hình")
    provider_name = st.selectbox("Provider", PROVIDERS, index=0)
    model = st.text_input("Model (để trống = mặc định của provider)", value="").strip() or None
    version = st.text_input("Version label", value=os.getenv("AGENT_VERSION", "v3")).strip() or "v3"
    history_window = st.slider("History window (cặp lượt)", 0, 10, 5)
    max_rounds = st.slider("Max tool rounds", 1, 8, 4)
    config = (provider_name, model, version, history_window, max_rounds)

    if "config" not in st.session_state:
        reset_session(config)
    if st.button("🔄 Cuộc trò chuyện mới", use_container_width=True) or st.session_state.config != config:
        reset_session(config)

    t = st.session_state.transcript
    st.divider()
    st.caption("Artifact đang chạy")
    st.code(
        f"artifact_version: {t.get('artifact_version')}\n"
        f"prompt_hash: {t.get('prompt_hash')}\n"
        f"tools_hash: {t.get('tools_hash')}",
        language="text",
    )
    st.caption("Transcript")
    st.code(str(st.session_state.transcript_path.relative_to(ROOT)), language="text")

    st.divider()
    st.caption("Tool agent có")
    try:
        for decl in load_tool_declarations(TOOLS_PATH):
            st.markdown(f"- `{decl['name']}`")
    except Exception as exc:
        st.error(f"Không đọc được tools.yaml: {exc}")


# ---------------------------------------------------------------- main
st.title("🔎 Research Agent — NhomSNN")
st.caption(
    "Tìm tin theo từ khóa / theo tài khoản X, tìm web, đọc URL, tổng hợp digest; "
    "hỏi lại khi thiếu thông tin và xin xác nhận trước khi gửi Telegram."
)

if not st.session_state.transcript["turns"]:
    st.markdown("**Thử nhanh:**")
    cols = st.columns(len(EXAMPLES))
    for col, example in zip(cols, EXAMPLES):
        if col.button(example, use_container_width=True):
            st.session_state.pending = example

for turn in st.session_state.transcript["turns"]:
    with st.chat_message("user"):
        st.markdown(turn["user"])
    with st.chat_message("assistant"):
        if turn.get("assistant_text"):
            st.markdown(turn["assistant_text"])
        render_turn_details(turn)

user_text = st.chat_input("Nhập yêu cầu research…") or st.session_state.pop("pending", None)
if user_text:
    with st.chat_message("user"):
        st.markdown(user_text)
    with st.chat_message("assistant"):
        with st.spinner("Agent đang chọn tool và chạy…"):
            run_turn(user_text)
    st.rerun()
