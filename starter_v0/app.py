from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import streamlit as st

# Setup page config
st.set_page_config(
    page_title="Research Agent — Multi-Tool Assistant",
    page_icon="🔬",
    layout="wide",
)

ROOT = Path(__file__).parent
ARTIFACTS_DIR = ROOT / "artifacts"

# Load environment & imports from starter_v0
from env_loader import load_lab_env
load_lab_env(ROOT)

from providers import make_provider
from tools import TOOL_FUNCTIONS, load_tool_declarations, to_openai_tools


def get_available_providers() -> list[str]:
    providers = []
    if os.getenv("OPENROUTER_API_KEY"):
        providers.append("openrouter")
    if os.getenv("GEMINI_API_KEY"):
        providers.append("gemini")
    if os.getenv("OPENAI_API_KEY"):
        providers.append("openai")
    if os.getenv("ANTHROPIC_API_KEY"):
        providers.append("anthropic")
    providers.append("ollama")
    # Default fallback to openrouter if none detected
    return providers if providers else ["openrouter", "gemini", "openai", "ollama"]


# Sidebar
with st.sidebar:
    st.title("⚙️ Cấu Hình Agent")
    st.markdown("---")

    avail_providers = get_available_providers()
    selected_provider = st.selectbox("Provider:", avail_providers, index=0)

    version = st.selectbox("Prompt/Tools Version:", ["v0", "v1", "v2", "v3"], index=3)

    st.markdown("### 🛠️ Tools Khả Dụng")
    tool_declarations = load_tool_declarations(ARTIFACTS_DIR / "tools.yaml")
    for tool in tool_declarations:
        is_bonus = tool["name"] in ["sentiment_analyzer", "send", "policy", "papers", "paper_text"]
        badge = "✨ Bonus" if is_bonus else "🔹 Core"
        with st.expander(f"{badge}: `{tool['name']}`"):
            st.caption(tool.get("description", ""))

    st.markdown("---")
    if st.button("🗑️ Xoá Lịch Sử Chat"):
        st.session_state.messages = []
        st.session_state.pending_confirmation = None
        st.rerun()


# Initialize state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "pending_confirmation" not in st.session_state:
    st.session_state.pending_confirmation = None


st.title("🔬 Research Agent with Tool Calling")
st.caption("Agent tự động tra cứu, tổng hợp tin tức, phân tích cảm xúc và gửi báo cáo an toàn.")

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "tool_events" in msg and msg["tool_events"]:
            for event in msg["tool_events"]:
                tool_name = event.get("tool", "unknown")
                args = event.get("args", {})
                result = event.get("result", {})
                with st.expander(f"🔧 Tool Call: `{tool_name}`", expanded=False):
                    st.markdown("**Arguments:**")
                    st.code(json.dumps(args, ensure_ascii=False, indent=2), language="json")
                    st.markdown("**Tool Output:**")
                    st.code(json.dumps(result, ensure_ascii=False, indent=2), language="json")


# Execute single tool call safely
def execute_tool(name: str, args: dict[str, Any]) -> dict[str, Any]:
    func = TOOL_FUNCTIONS.get(name)
    if not func:
        return {"error": "unknown_tool", "message": f"Tool '{name}' không tồn tại."}
    try:
        return func(**args)
    except Exception as exc:
        return {"error": type(exc).__name__, "message": str(exc)}


# Pending Action Guardrail confirmation UI
if st.session_state.pending_confirmation:
    conf = st.session_state.pending_confirmation
    st.warning(f"⚠️ **Xác Nhận Hành Động An Toàn (Guardrail):** Agent chuẩn bị gọi tool `{conf['tool']}`.")
    st.info(f"Nội dung: {conf.get('text', '')}")
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("✅ Đồng Ý Gửi", type="primary"):
            with st.spinner("Đang thực hiện gửi..."):
                args = dict(conf["args"])
                args["confirmed"] = True
                exec_res = execute_tool(conf["tool"], args)
                st.session_state.pending_confirmation = None
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"Đã gửi thành công! Kết quả: `{exec_res.get('status')}`",
                    "tool_events": [{"tool": conf["tool"], "args": args, "result": exec_res}]
                })
                st.rerun()
    with col2:
        if st.button("❌ Huỷ Bỏ"):
            st.session_state.pending_confirmation = None
            st.session_state.messages.append({
                "role": "assistant",
                "content": "Đã huỷ bỏ hành động gửi theo yêu cầu của bạn.",
                "tool_events": []
            })
            st.rerun()


# Chat input
if user_prompt := st.chat_input("Nhập câu hỏi hoặc yêu cầu nghiên cứu của bạn..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.markdown(user_prompt)

    # Process with agent
    with st.chat_message("assistant"):
        with st.spinner("Agent đang xử lý và lựa chọn tools..."):
            try:
                system_prompt = (ARTIFACTS_DIR / "system_prompt.md").read_text(encoding="utf-8")
                openai_tools = to_openai_tools(tool_declarations)
                provider = make_provider(selected_provider)

                # Prepare conversation context
                history_window = 6
                recent_messages = []
                for m in st.session_state.messages[-history_window:]:
                    recent_messages.append({"role": m["role"], "content": m["content"]})

                messages = [
                    {"role": "system", "content": system_prompt},
                    *recent_messages,
                ]

                # Run provider completion
                response = provider.complete(messages, openai_tools, temperature=0.0)
                tool_calls = response.tool_calls
                tool_events = []

                if not tool_calls:
                    assistant_text = response.text or "Tôi không có thêm thông tin cho yêu cầu này."
                    st.markdown(assistant_text)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": assistant_text,
                        "tool_events": []
                    })
                else:
                    # Execute each tool call
                    needs_user_confirmation = False
                    for call in tool_calls:
                        # Guardrail check for action tool 'send'
                        if call.name == "send" and not call.args.get("confirmed", False):
                            st.session_state.pending_confirmation = {
                                "tool": "send",
                                "args": call.args,
                                "text": call.args.get("text", "")
                            }
                            needs_user_confirmation = True
                            st.warning("Agent yêu cầu bạn xác nhận trước khi gửi dữ liệu ra bên ngoài.")
                            st.rerun()

                        with st.status(f"Đang thực thi `{call.name}`...", expanded=True) as status:
                            st.write(f"**Arguments:** `{call.args}`")
                            res = execute_tool(call.name, call.args)
                            st.write(f"**Result:** `{res}`")
                            status.update(label=f"Đã hoàn thành `{call.name}`", state="complete")

                        tool_events.append({"tool": call.name, "args": call.args, "result": res})

                    # Second turn to summarize tool output
                    summary_messages = [
                        {"role": "system", "content": system_prompt},
                        *recent_messages,
                        {"role": "assistant", "content": response.text or "Đã gọi các tool cần thiết."},
                        {
                            "role": "user",
                            "content": f"Dữ liệu kết quả từ các tools:\n{json.dumps(tool_events, ensure_ascii=False, indent=2)}\n\nHãy tổng hợp câu trả lời đầy đủ, chính xác dựa trên kết quả tool trên."
                        }
                    ]
                    final_response = provider.complete(summary_messages, temperature=0.2)
                    final_text = final_response.text or "Đã xử lý xong các tools."

                    st.markdown(final_text)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": final_text,
                        "tool_events": tool_events
                    })

            except Exception as e:
                err_msg = f"Đã xảy ra lỗi: {type(e).__name__} - {str(e)}"
                st.error(err_msg)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": err_msg,
                    "tool_events": []
                })

