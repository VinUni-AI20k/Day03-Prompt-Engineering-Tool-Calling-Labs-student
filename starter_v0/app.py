import json
from pathlib import Path

import streamlit as st

from chat import run_model_tool_loop
from env_loader import load_lab_env
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version


ROOT = Path(__file__).parent
load_lab_env(ROOT)

st.set_page_config(page_title="Research Agent", page_icon="🔎")
st.title("🔎 Research Agent")
st.caption("Tìm kiếm, đọc nguồn và tổng hợp thông tin bằng tools.")

with st.sidebar:
    st.header("Cấu hình")

    provider_name = st.selectbox(
        "Provider",
        ["openrouter", "openai", "anthropic", "gemini", "ollama"],
    )
    model = st.text_input("Model", placeholder="Để trống dùng mặc định")
    version = st.text_input("Version", value="v0")

    if st.button("Xóa hội thoại"):
        st.session_state.pop("messages", None)
        st.session_state.pop("turns", None)
        st.rerun()

# Mỗi phiên trình duyệt có lịch sử riêng.
if "messages" not in st.session_state:
    st.session_state.messages = []

if "turns" not in st.session_state:
    st.session_state.turns = []

# Hiển thị lại hội thoại sau mỗi lần Streamlit chạy lại.
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

user_input = st.chat_input("Bạn muốn nghiên cứu gì?")

if user_input:
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        try:
            prompt_path = ROOT / "artifacts" / "system_prompt.md"
            tools_path = ROOT / "artifacts" / "tools.yaml"

            system_prompt = prompt_path.read_text(encoding="utf-8")
            declarations = load_tool_declarations(tools_path)
            tools = to_openai_tools(declarations)
            provider = make_provider(provider_name)

            artifact = build_artifact_version(
                version, prompt_path, tools_path
            )

            messages = [
                {"role": "system", "content": system_prompt},
                *st.session_state.messages[-10:],
                {"role": "user", "content": user_input},
            ]

            with st.spinner("Agent đang xử lý..."):
                result = run_model_tool_loop(
                    provider=provider,
                    messages=messages,
                    tools=tools,
                    model=model.strip() or None,
                    max_tool_rounds=4,
                )

            answer = result["assistant_text"]
            st.markdown(answer)

            st.session_state.messages.extend([
                {"role": "user", "content": user_input},
                {"role": "assistant", "content": answer},
            ])

            st.session_state.turns.append({
                "user": user_input,
                "provider": provider_name,
                "model": model.strip() or getattr(
                    provider, "default_model", None
                ),
                **artifact_version_dict(artifact),
                **result,
            })

        except Exception as exc:
            st.error(f"Không xử lý được yêu cầu: {exc}")

if st.session_state.turns:
    with st.expander("Chi tiết tool của lượt gần nhất"):
        st.json(st.session_state.turns[-1])

    st.download_button(
        "Tải lịch sử UI (JSON)",
        data=json.dumps(
            {"turns": st.session_state.turns},
            ensure_ascii=False,
            indent=2,
            default=str,
        ),
        file_name="ui_chat.json",
        mime="application/json",
    )