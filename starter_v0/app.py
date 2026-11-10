from __future__ import annotations

import os

import streamlit as st

from chat import ARTIFACTS_DIR, run_model_tool_loop, trim_history
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools


st.set_page_config(page_title="Research Agent", page_icon="🔎")
st.title("Research Agent")
st.caption("Tìm nguồn, đọc nội dung, lọc URL trùng và trình bày kết quả nghiên cứu.")
st.sidebar.markdown("**Thử hỏi**\n\n- Tìm hai tin web về pin thể rắn trong tuần này.\n- Lọc link trùng trong danh sách nguồn của tôi.")

turns = st.session_state.setdefault("turns", [])
if st.sidebar.button("Cuộc trò chuyện mới"):
    turns.clear()
    st.rerun()

for turn in turns:
    st.chat_message("user").text(turn["question"])
    with st.chat_message("assistant"):
        if turn["provider_error"]:
            st.error(turn["provider_error"])
        else:
            st.markdown(turn["answer"])
            for tool_name, error in turn["tool_errors"]:
                st.warning(f"Tool `{tool_name}` gặp lỗi `{error}`.")
            if turn["tools"]:
                st.caption("Tool đã gọi · " + ", ".join(turn["tools"]))

question = st.chat_input("Nhập yêu cầu nghiên cứu…", max_chars=4000)
if question and question.strip():
    question = question.strip()
    st.chat_message("user").text(question)
    history = []
    for turn in turns:
        if not turn["provider_error"]:
            history.extend([
                {"role": "user", "content": turn["question"]},
                {"role": "assistant", "content": turn["answer"]},
            ])

    provider_name = os.getenv("DAY03_UI_PROVIDER", "openrouter").strip().lower()
    current = {"question": question, "answer": "", "provider_error": "", "tools": [], "tool_errors": []}
    with st.spinner("Agent đang xử lý yêu cầu…"):
        try:
            system_prompt = (ARTIFACTS_DIR / "system_prompt.md").read_text(encoding="utf-8")
            declarations = load_tool_declarations(ARTIFACTS_DIR / "tools.yaml")
            result = run_model_tool_loop(
                provider=make_provider(provider_name),
                messages=[
                    {"role": "system", "content": system_prompt},
                    *trim_history(history, 5),
                    {"role": "user", "content": question},
                ],
                tools=to_openai_tools(declarations),
                model=None,
                max_tool_rounds=4,
            )
        except Exception as exc:
            current["provider_error"] = (
                f"Không chạy được lượt này ({type(exc).__name__}). "
                "Kiểm tra cấu hình provider trong .env và thử lại."
            )
        else:
            current["answer"] = result["assistant_text"] or "Agent chưa trả lời yêu cầu này."
            for event in result["tool_events"]:
                current["tools"].append(event["tool"])
                if error := event["result"].get("error"):
                    current["tool_errors"].append((event["tool"], error))

    turns.append(current)
    st.rerun()
