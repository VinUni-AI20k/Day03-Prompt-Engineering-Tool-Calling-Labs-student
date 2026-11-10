"""Streamlit UI for the Research Agent. Put this file next to chat.py.

Run:          streamlit run app.py
Public link:  cloudflared tunnel --url http://localhost:8501
"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path

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

SAMPLE_QUERIES = [  # replace with the sample questions from section A3 of the group report
    "Tweet mới nhất của Sam Altman là gì?",
    "Tin tức AI hôm nay có gì nổi bật?",
    "Tóm tắt 5 tweet mới nhất giúp mình",
    "Đăng bản tin này lên Telegram giúp mình",
]
TRANSCRIPTS_DIR = ROOT / "transcripts"

st.set_page_config(page_title="Research Agent", page_icon="🔎")
st.title("Research Agent")

# ---------------- sidebar settings ----------------
with st.sidebar:
    st.subheader("Cấu hình")
    provider_name = st.selectbox(
        "Provider", ["openrouter", "openai", "anthropic", "gemini", "ollama"]
    )
    model = st.text_input("Model (để trống = mặc định)", value="") or None
    version = st.text_input("Version label", value="v3")
    window = st.number_input("History window", 1, 10, 5)
    if st.button("Cuộc trò chuyện mới", use_container_width=True):
        for k in ("messages", "history", "transcript", "transcript_path", "pending"):
            st.session_state.pop(k, None)
        st.rerun()


@st.cache_resource
def get_provider(name: str):
    return make_provider(name)


def init_session():
    if "messages" in st.session_state:
        return
    system_prompt_path = ARTIFACTS_DIR / "system_prompt.md"
    tools_path = ARTIFACTS_DIR / "tools.yaml"
    av = build_artifact_version(version, system_prompt_path, tools_path)
    tid = "_".join(
        [safe_slug(version), safe_slug(provider_name), datetime.now().strftime("%Y%m%dT%H%M%S%f")]
    )
    st.session_state.messages = []  # for display: {"role","content","events"}
    st.session_state.history = []  # same format as chat.py: plain user/assistant text
    st.session_state.pending = None  # question text if the last reply is a yes/no confirmation
    st.session_state.transcript_path = TRANSCRIPTS_DIR / f"{tid}.transcript.json"
    st.session_state.transcript = {
        "transcript_id": tid,
        **artifact_version_dict(av),
        "provider": provider_name,
        "model": model,
        "system_prompt": str(system_prompt_path),
        "tools": str(tools_path),
        "history_window": window,
        "max_tool_rounds": 4,
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "turns": [],
    }


def handle_user_input(user_text: str):
    init_session()
    ss = st.session_state
    system_prompt = (ARTIFACTS_DIR / "system_prompt.md").read_text(encoding="utf-8")
    tools = to_openai_tools(load_tool_declarations(ARTIFACTS_DIR / "tools.yaml"))
    messages = [
        {"role": "system", "content": system_prompt},
        *trim_history(ss.history, int(window)),
        {"role": "user", "content": user_text},
    ]
    turn = {
        "turn_index": len(ss.transcript["turns"]) + 1,
        "started_at": now_iso(),
        "user": user_text,
        "status": "started",
        "assistant_text": None,
        "rounds": [],
        "tool_events": [],
    }
    ss.messages.append({"role": "user", "content": user_text, "events": []})
    ss.pending = None
    try:
        result = run_model_tool_loop(
            provider=get_provider(provider_name),
            messages=messages,
            tools=tools,
            model=model,
            max_tool_rounds=4,
        )
        turn.update(result)
        reply = result["assistant_text"]
        ss.history += [
            {"role": "user", "content": user_text},
            {"role": "assistant", "content": reply},
        ]
        # a clarify with response_type=yes_no -> show confirm buttons
        for ev in result["tool_events"]:
            res = ev.get("result", {})
            if isinstance(res, dict) and res.get("awaiting_user"):
                if (ev.get("args") or {}).get("response_type") == "yes_no":
                    ss.pending = reply
        ss.messages.append({"role": "assistant", "content": reply, "events": result["tool_events"]})
    except Exception as exc:
        turn.update({"status": "provider_error", "error": f"{type(exc).__name__}: {exc}"})
        ss.messages.append(
            {"role": "assistant", "content": f"Lỗi: {turn['error']}", "events": []}
        )
    turn["ended_at"] = now_iso()
    ss.transcript["turns"].append(turn)
    write_transcript(ss.transcript_path, ss.transcript)


init_session()

with st.sidebar:
    st.subheader("Câu hỏi mẫu")
    for q in SAMPLE_QUERIES:
        if st.button(q, use_container_width=True):
            handle_user_input(q)
            st.rerun()
    st.caption(f"Transcript: {st.session_state.transcript_path.name}")

# ---------------- chat display ----------------
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.write(m["content"])
        for ev in m["events"]:
            with st.expander(f"🔧 {ev['tool']}"):
                st.json({"args": ev["args"], "result": ev["result"]}, expanded=False)

if st.session_state.pending:
    c1, c2 = st.columns(2)
    if c1.button("✅ Đồng ý", use_container_width=True):
        handle_user_input("Đồng ý")
        st.rerun()
    if c2.button("❌ Không", use_container_width=True):
        handle_user_input("Không")
        st.rerun()

if prompt := st.chat_input("Nhập yêu cầu..."):
    handle_user_input(prompt)
    st.rerun()