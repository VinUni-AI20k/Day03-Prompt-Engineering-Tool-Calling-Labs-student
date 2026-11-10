import os
from pathlib import Path

import streamlit as st

from chat import run_model_tool_loop
from env_loader import load_lab_env
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools


ROOT = Path(__file__).parent
load_lab_env(ROOT)
# Public demo must not have Telegram credentials.
os.environ.pop("TELEGRAM_BOT_TOKEN", None)
os.environ.pop("TELEGRAM_CHAT_ID", None)
st.set_page_config(page_title="Research Agent", page_icon="🔎")
st.title("🔎 Research Agent")
st.caption("Tìm nguồn, tổng hợp thông tin và xem các tool agent sử dụng.")

if "messages" not in st.session_state:
    st.session_state.messages = []

if "history" not in st.session_state:
    st.session_state.history = []

api_key_ready = bool(os.getenv("OPENROUTER_API_KEY"))
if not api_key_ready:
    st.info("Chưa có OPENROUTER_API_KEY trong .env. Giao diện đã sẵn sàng; cần key để chat với agent.")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])
        if message.get("tool_events"):
            with st.expander("Tool đã sử dụng"):
                st.json(message["tool_events"])

user_text = st.chat_input(
    "Nhập câu hỏi nghiên cứu...",
    disabled=not api_key_ready,
)

if user_text:
    st.session_state.messages.append({"role": "user", "content": user_text})

    try:
        prompt = (ROOT / "artifacts/system_prompt.md").read_text(encoding="utf-8")
        declarations = load_tool_declarations(ROOT / "artifacts/tools.yaml")
        # Do not offer the action tool in the public UI.
        declarations = [tool for tool in declarations if tool["name"] != "send"]
        tools = to_openai_tools(declarations)
        provider = make_provider("openrouter")

        messages = [
            {"role": "system", "content": prompt},
            *st.session_state.history[-10:],
            {"role": "user", "content": user_text},
        ]

        with st.spinner("Agent đang xử lý..."):
            result = run_model_tool_loop(
                provider=provider,
                messages=messages,
                tools=tools,
                model=None,
                max_tool_rounds=4,
            )

        answer = result["assistant_text"]
        st.session_state.messages.append({
            "role": "assistant",
            "content": answer,
            "tool_events": result["tool_events"],
        })
        st.session_state.history.extend([
            {"role": "user", "content": user_text},
            {"role": "assistant", "content": answer},
        ])
    except Exception as exc:
        st.session_state.messages.append({
            "role": "assistant",
            "content": f"Không thể xử lý: {exc}",
        })

    st.rerun()