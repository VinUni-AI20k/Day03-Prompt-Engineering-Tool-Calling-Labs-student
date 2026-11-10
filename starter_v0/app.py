from __future__ import annotations

import streamlit as st

from chat import ARTIFACTS_DIR, run_model_tool_loop, trim_history
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import build_artifact_version

PROVIDER = "openrouter"
VERSION_LABEL = "ui"
HISTORY_WINDOW = 5
MAX_TOOL_ROUNDS = 4
SYSTEM_PROMPT_PATH = ARTIFACTS_DIR / "system_prompt.md"
TOOLS_PATH = ARTIFACTS_DIR / "tools.yaml"

st.set_page_config(page_title="Research Agent", page_icon="🔎")


@st.cache_resource
def get_provider(name: str):
    return make_provider(name)


def render_events(events):
    for event in events:
        result = event.get("result", {})
        failed = isinstance(result, dict) and bool(result.get("error"))
        with st.expander(f"{'❌' if failed else '🔧'} {event.get('tool')}"):
            st.caption("Tham số")
            st.json(event.get("args", {}))
            st.caption("Kết quả")
            st.json(result)


system_prompt = SYSTEM_PROMPT_PATH.read_text(encoding="utf-8")
openai_tools = to_openai_tools(load_tool_declarations(TOOLS_PATH))
artifact = build_artifact_version(VERSION_LABEL, SYSTEM_PROMPT_PATH, TOOLS_PATH)

st.title("Research Agent")
st.caption(f"artifact_version={artifact.artifact_version}")

if "history" not in st.session_state:
    st.session_state.history = []
    st.session_state.messages = []

if st.sidebar.button("Xoá hội thoại"):
    st.session_state.history = []
    st.session_state.messages = []
    st.rerun()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["text"])
        render_events(message["events"])

user_text = st.chat_input("Hỏi research agent...")
if user_text:
    with st.chat_message("user"):
        st.write(user_text)
    messages = [
        {"role": "system", "content": system_prompt},
        *trim_history(st.session_state.history, HISTORY_WINDOW),
        {"role": "user", "content": user_text},
    ]
    st.session_state.messages.append({"role": "user", "text": user_text, "events": []})
    try:
        with st.spinner("Đang xử lý..."):
            result = run_model_tool_loop(
                provider=get_provider(PROVIDER),
                messages=messages,
                tools=openai_tools,
                model=None,
                max_tool_rounds=MAX_TOOL_ROUNDS,
            )
        reply = result["assistant_text"]
        events = result["tool_events"]
        st.session_state.history += [
            {"role": "user", "content": user_text},
            {"role": "assistant", "content": reply},
        ]
    except Exception as exc:
        reply = f"Lỗi provider: {type(exc).__name__}: {str(exc)[:300]}"
        events = []
    st.session_state.messages.append({"role": "assistant", "text": reply, "events": events})
    st.rerun()