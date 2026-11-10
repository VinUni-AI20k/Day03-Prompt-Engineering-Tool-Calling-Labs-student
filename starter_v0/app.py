"""Run: python -m streamlit run app.py"""
from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path
from uuid import uuid4

import streamlit as st

from chat import run_model_tool_loop
from env_loader import load_lab_env
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version

ROOT = Path(__file__).resolve().parent
load_lab_env(ROOT)
st.set_page_config(page_title="NoName · Research Desk", page_icon="🔎", layout="wide")
st.markdown("""<style>
.stApp {background: #f5f4ef; color: #182725;}
.block-container {max-width: 1060px; padding-top: 2.8rem;}
h1 {letter-spacing: -.05em; font-weight: 700;}
[data-testid="stChatMessage"] {border: 1px solid #dce3dd; border-radius: 16px; background: #fff;}
</style>""", unsafe_allow_html=True)

if "history" not in st.session_state:
    st.session_state.history = []
    st.session_state.turns = []
    st.session_state.session_id = uuid4().hex

with st.sidebar:
    st.caption("NHÓM NONAME / DAY 03")
    st.title("Research Desk")
    st.write("Tìm nguồn. Đọc bằng chứng. Tổng hợp rõ ràng.")
    st.divider()
    st.markdown("**Bạn có thể**\n\nTìm tin trên web, đọc URL, xem bài đăng X, tra chính sách, tìm paper và loại nguồn trùng.")
    st.caption("Chế độ nghiên cứu: giao diện này không gửi tin ra ngoài.")
    if st.button("Bắt đầu cuộc trò chuyện mới", use_container_width=True):
        for key in ["history", "turns", "session_id"]:
            del st.session_state[key]
        st.rerun()
    if st.session_state.turns:
        st.download_button("Tải cuộc trò chuyện", json.dumps(st.session_state.turns, ensure_ascii=False, indent=2),
                           "research-conversation.json", "application/json")

st.caption("NGHIÊN CỨU CÓ NGUỒN • NONAME RESEARCH AGENT")
st.title("Từ câu hỏi đến bằng chứng.")
st.write("Một nơi để tìm, đọc và sắp xếp thông tin cho bản tin của bạn.")
if not st.session_state.history:
    columns = st.columns(3)
    examples = ["Tin GPU hôm nay có gì nổi bật?", "Chính sách nội bộ về dữ liệu cá nhân là gì?",
                'Loại link trùng: [{"url":"https://example.com/a"},{"url":"https://example.com/a"}]']
    for column, example in zip(columns, examples):
        with column:
            st.info(example)

for message in st.session_state.history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("Bạn muốn tìm hiểu điều gì?")
if prompt:
    with st.chat_message("user"):
        st.markdown(prompt)
    system_path = ROOT / "artifacts/system_prompt.md"
    tools_path = ROOT / "artifacts/tools.yaml"
    system_prompt = system_path.read_text(encoding="utf-8")
    declarations = load_tool_declarations(tools_path)
    # Public research UI never exposes the external-delivery action to the model.
    declarations = [item for item in declarations if item["name"] != "send"]
    provider = make_provider("openrouter")
    with st.chat_message("assistant"):
        try:
            with st.spinner("Đang đọc và đối chiếu thông tin…"):
                result = run_model_tool_loop(
                    provider=provider,
                    messages=[{"role": "system", "content": system_prompt + "\nThis UI cannot send externally. Explain this limitation if asked to send."},
                              *st.session_state.history[-10:], {"role": "user", "content": prompt}],
                    tools=to_openai_tools(declarations), model=None, max_tool_rounds=4,
                )
            answer = result["assistant_text"]
            st.markdown(answer)
            events = result.get("tool_events", [])
            if events:
                with st.expander("Nguồn và kết quả tra cứu"):
                    for event in events:
                        st.json({"tool": event.get("tool"), "result": event.get("result")}, expanded=False)
            version = build_artifact_version("v3", system_path, tools_path)
            st.session_state.turns.append({"user": prompt, **result})
            st.session_state.history.extend([{"role": "user", "content": prompt}, {"role": "assistant", "content": answer}])
            transcript = {"transcript_id": st.session_state.session_id, "source": "streamlit",
                          **artifact_version_dict(version), "provider": "openrouter", "model": provider.default_model,
                          "ui_tools_excluded": ["send"], "ui_system_suffix": "This UI cannot send externally. Explain this limitation if asked to send.",
                          "updated_at": datetime.now().isoformat(), "turns": st.session_state.turns}
            folder = ROOT / "transcripts"
            folder.mkdir(exist_ok=True)
            (folder / f"ui_{st.session_state.session_id}.transcript.json").write_text(
                json.dumps(transcript, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception:
            st.error("Chưa xử lý được yêu cầu. Hãy kiểm tra kết nối, cấu hình dịch vụ và hạn mức rồi thử lại.")
