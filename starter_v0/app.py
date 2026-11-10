"""Research desk UI for the team's main branch (14 registered tools)."""
from __future__ import annotations

import hmac
import os

import streamlit as st

from providers import make_provider
from tools import load_tool_declarations
from ui_support import TOOLS, new_session, redact, run_turn, transcript_json

st.set_page_config(page_title="Hehehe · Research desk", page_icon=":material/travel_explore:", layout="wide")

st.title("Research desk")
st.caption("Hehehe · L3B · Tìm nguồn, đối chiếu và tổng hợp nghiên cứu")

access_code = os.getenv("DEMO_ACCESS_CODE", "")
if access_code and not st.session_state.get("authorized", False):
    st.info("Nhập mã nhóm cung cấp để dùng bản demo.")
    with st.form("access"):
        supplied = st.text_input("Mã dùng thử", type="password", key="access_code")
        submitted = st.form_submit_button("Mở bàn nghiên cứu", key="unlock")
    if submitted:
        if hmac.compare_digest(supplied.encode(), access_code.encode()):
            st.session_state.authorized = True
            st.rerun()
        else:
            st.error("Mã chưa đúng.")
    st.stop()

if "conversation" not in st.session_state:
    st.session_state.conversation = new_session()
conversation = st.session_state.conversation
declarations = load_tool_declarations(TOOLS)

with st.sidebar:
    st.subheader("Bàn nghiên cứu của nhóm")
    st.caption("OpenAI · gpt-4o-mini")
    st.metric("Công cụ sẵn có", len(declarations))
    st.write("Tìm web, bài đăng, repository GitHub, paper và chính sách nội bộ. Đọc URL, lọc ngày, loại trùng và so sánh nguồn.")
    with st.expander("Danh sách công cụ"):
        for declaration in declarations:
            st.write(f"• {declaration['name']}")
    st.caption("20 lượt/phiên · tối đa 6000 ký tự/lượt")
    st.download_button("Tải transcript JSON", data=transcript_json(conversation),
                       file_name=f"{conversation['transcript_id']}.transcript.json",
                       mime="application/json", key="download", width="stretch")
    if st.button("Cuộc trò chuyện mới", key="reset", width="stretch"):
        st.session_state.conversation = new_session()
        st.rerun()
    st.caption("Bản ghi phiên cũ vẫn được lưu trên máy chạy demo.")

if not conversation["turns"]:
    st.subheader("Bạn muốn nghiên cứu điều gì?")
    st.write("Nhập câu hỏi, URL hoặc danh sách nguồn. Agent sẽ hỏi lại khi cần dữ liệu và xin xác nhận trước khi gửi Telegram.")
    with st.expander("Câu hỏi mẫu", expanded=True):
        st.markdown("""- Tìm 3 repository Python về research agent trên GitHub, sắp theo số sao.
- Theo chính sách nội bộ, có được đưa dữ liệu khách hàng vào AI bên ngoài không?
- Loại trùng theo URL: [{"title":"A","url":"https://example.com/a?utm_source=demo"},{"title":"B","url":"https://example.com/a"}].
- Lấy 2 bài đăng mới nhất giúp tôi. *(Lượt sau bổ sung tài khoản.)*
- Tôi muốn gửi 'Bản tin demo của nhóm Hehehe' lên Telegram. Hãy hỏi xác nhận trước. *(Sau đó có thể hủy.)*""")

for turn in conversation["turns"]:
    with st.chat_message("user"):
        st.write(turn["user"])
    with st.chat_message("assistant"):
        if turn["status"] == "provider_error":
            st.error(turn.get("error", "Provider chưa trả kết quả. Hãy thử lại."))
        else:
            st.write(turn["assistant_text"])
        errors = [e for e in turn["tool_events"] if isinstance(e.get("result"), dict) and e["result"].get("error")]
        if errors:
            st.warning("Có công cụ trả lỗi. Xem chi tiết bên dưới; kết quả có thể chưa đầy đủ.")
        if turn["tool_events"]:
            with st.expander("Công cụ đã chạy và kết quả"):
                st.json(redact(turn["tool_events"]))
        if turn["status"] == "waiting_for_user":
            st.caption("Đang chờ bạn bổ sung hoặc xác nhận.")
        elif turn["status"] == "max_tool_rounds":
            st.warning("Đã đạt giới hạn 4 vòng công cụ. Bạn có thể thu hẹp yêu cầu.")

prompt = st.chat_input("Nhập câu hỏi nghiên cứu…", key="question", max_chars=6000,
                       disabled=len(conversation["turns"]) >= 20, submit_mode="disable")
if prompt:
    try:
        with st.spinner("Đang tìm và xử lý nguồn…"):
            run_turn(conversation, prompt, make_provider("openai"))
    except (ValueError, OSError) as exc:
        st.error(str(redact(str(exc))))
    else:
        st.rerun()
