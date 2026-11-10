"""Local research chat and tool playground: python -m streamlit run app.py."""
from __future__ import annotations

import json
import os
import traceback
from pathlib import Path
from uuid import uuid4

import streamlit as st

from chat import execute_tool_call, now_iso, run_model_tool_loop, write_transcript
from providers import make_provider
from tools import TOOL_FUNCTIONS, load_tool_declarations, to_openai_tools
from tools.send.tool import approve_message, send_telegram
from versioning import artifact_version_dict, build_artifact_version

ROOT = Path(__file__).resolve().parent
st.set_page_config(page_title="Research Lab", page_icon="🔎", layout="wide")
st.title("🔎 Research Lab")
st.caption("Thử tool • Chat với agent • Xác nhận trước khi gửi Telegram")

if "lab" not in st.session_state:
    st.session_state.lab = {"id": uuid4().hex, "created_at": now_iso(), "turns": []}
    st.session_state.history = []
    st.session_state.pending = None
    st.session_state.events = []


def record(user, result, version="ui-tools"):
    evidence = artifact_version_dict(build_artifact_version(
        version, ROOT / "artifacts/system_prompt.md", ROOT / "artifacts/tools.yaml"))
    st.session_state.lab["turns"].append({
        "user": user, "ended_at": now_iso(), **evidence, **result})
    write_transcript(ROOT / "transcripts" / f"ui_{st.session_state.lab['id']}.transcript.json",
                     st.session_state.lab)


def web_execute(call):
    if call.name != "send":
        return execute_tool_call(call)
    text = call.args.get("text")
    if not isinstance(text, str) or not text.strip() or len(text) > 4096:
        result = {"error": "ValueError", "message": "Nội dung cần có 1–4096 ký tự."}
    else:
        st.session_state.pending = {"text": text, "demo": False}
        result = {"status": "needs_confirmation", "awaiting_user": True,
                  "question": "Hãy xem nội dung và chọn Xác nhận gửi hoặc Hủy bên dưới."}
    return {"tool": "send", "args": call.args, "result": result}


with st.sidebar:
    st.header("Cấu hình")
    provider_name = st.selectbox("Nhà cung cấp", ["openai", "openrouter", "gemini", "anthropic", "ollama"])
    model = st.text_input("Model (để trống dùng mặc định)")
    version = st.text_input("Phiên bản", value="v0")
    st.caption("Key được đọc từ .env trên máy. Không nhập key vào chat.")
    for label, env in [("Tavily", "TAVILY_API_KEY"), ("Telegram bot", "TELEGRAM_BOT_TOKEN"),
                       ("Telegram chat", "TELEGRAM_CHAT_ID")]:
        st.write(f"{'✅' if os.getenv(env) else '⚪'} {label}")
    st.download_button("Tải transcript JSON", json.dumps(st.session_state.lab, ensure_ascii=False, indent=2),
                       file_name="research.transcript.json", mime="application/json")

chat_tab, tools_tab = st.tabs(["Chat với agent", "Thử tool trực tiếp"])
with tools_tab:
    st.subheader("Kiểm tra tool không cần gọi AI")
    tool_name = st.selectbox("Tool", ["deduplicate", "citation_audit", "lookup"])
    if tool_name == "lookup":
        query = st.text_input("Từ khóa tìm kiếm", value="AI agent evaluation")
        st.caption("Chạy tìm kiếm dùng quota Tavily.")
    else:
        raw = st.text_area("Danh sách nguồn (JSON)", value=json.dumps([
            {"title": "Nguồn A", "source": "Example", "url": "https://example.com/article"},
            {"title": "Nguồn A trùng", "source": "Example", "url": "https://example.com/article?utm_source=test"}
        ], ensure_ascii=False, indent=2), height=220)
    if st.button("Chạy tool", disabled=st.session_state.pending is not None):
        try:
            args = {"query": query, "max_results": 1} if tool_name == "lookup" else {"items": json.loads(raw)}
            with st.spinner("Đang chạy tool…"):
                result = TOOL_FUNCTIONS[tool_name](**args)
            event = {"tool": tool_name, "args": args, "result": result}
            st.session_state.events = [event]
            record(f"Direct tool: {tool_name}", {"tool_events": [event]})
        except (ValueError, TypeError) as exc:
            st.error(f"JSON không hợp lệ: {exc}")

    st.divider()
    st.subheader("Thử bước xác nhận Telegram")
    draft = st.text_area("Nội dung xem trước", value="Xin chào nhóm! Đây là tin nhắn thử.")
    demo = st.checkbox("Chỉ mô phỏng (không gửi mạng)", value=True)
    if st.button("Xem trước gửi", disabled=st.session_state.pending is not None):
        if not draft.strip() or len(draft) > 4096:
            st.error("Nội dung cần có 1–4096 ký tự.")
        else:
            st.session_state.pending = {"text": draft, "demo": demo}
            st.rerun()

with chat_tab:
    for message in st.session_state.history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    prompt = st.chat_input("Nhập yêu cầu research…", disabled=st.session_state.pending is not None)
    if prompt:
        st.session_state.history.append({"role": "user", "content": prompt})
        system = (ROOT / "artifacts/system_prompt.md").read_text(encoding="utf-8")
        system += "\nFor Telegram, propose send with exact text; never claim sent before tool success. Local citation_audit checks metadata only; deduplicate removes repeated source URLs."
        try:
            with st.spinner("Agent đang xử lý…"):
                result = run_model_tool_loop(
                    provider=make_provider(provider_name),
                    messages=[{"role": "system", "content": system}, *st.session_state.history[-10:]],
                    tools=to_openai_tools(load_tool_declarations(ROOT / "artifacts/tools.yaml")),
                    model=model.strip() or None, max_tool_rounds=4, execute_call=web_execute)
            st.session_state.events = result["tool_events"]
            st.session_state.history.append({"role": "assistant", "content": result["assistant_text"]})
            record(prompt, {"provider": provider_name, "model": model or None, **result}, version or "v0")
        except Exception as exc:
            # SDK exceptions can include request details; keep credentials off the UI.
            if isinstance(exc, UnicodeEncodeError):
                frames = traceback.extract_tb(exc.__traceback__)
                st.session_state.encoding_diagnostic = {
                    "encoding": exc.encoding,
                    "frames": [f"{Path(frame.filename).name}:{frame.lineno} ({frame.name})" for frame in frames],
                }
            st.session_state.history.append({"role": "assistant", "content":
                f"Không hoàn tất yêu cầu ({type(exc).__name__}). Kiểm tra key, model và kết nối."})
        st.rerun()

if st.session_state.pending:
    pending = dict(st.session_state.pending)
    st.warning("Đang chờ bạn xác nhận. Nội dung dưới đây được giữ cố định.")
    st.text(pending["text"])
    st.caption("Mô phỏng: không gửi mạng." if pending["demo"] else "Gửi thật tới TELEGRAM_CHAT_ID đã cấu hình trong .env.")
    yes, no = st.columns(2)
    if yes.button("Xác nhận gửi", type="primary"):
        # Consume pending action before executing: reruns cannot replay this send.
        st.session_state.pending = None
        if pending["demo"]:
            result = {"status": "simulated", "message": "Đã xác nhận mô phỏng; chưa gửi Telegram."}
        else:
            with approve_message(pending["text"]):
                result = send_telegram(pending["text"], confirmed=True)
        event = {"tool": "send", "args": {"text": pending["text"], "confirmed": True}, "result": result}
        st.session_state.events = [event]
        st.session_state.history.append({"role": "assistant", "content": f"Kết quả gửi: {result.get('status', 'error')}"})
        record("UI confirmation", {"tool_events": [event]})
        st.rerun()
    if no.button("Hủy gửi"):
        st.session_state.pending = None
        event = {"tool": "send", "result": {"status": "cancelled"}}
        st.session_state.events = [event]
        st.session_state.history.append({"role": "assistant", "content": "Đã hủy gửi."})
        record("UI cancellation", {"tool_events": [event]})
        st.rerun()

if st.session_state.events:
    with st.expander("Tool call và kết quả gần nhất", expanded=True):
        st.json(st.session_state.events)

if st.session_state.get("encoding_diagnostic"):
    with st.expander("Chi tiết vị trí lỗi mã hóa (không chứa key)"):
        st.json(st.session_state.encoding_diagnostic)
