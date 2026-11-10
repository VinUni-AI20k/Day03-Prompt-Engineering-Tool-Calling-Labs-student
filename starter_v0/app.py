"""Streamlit UI cho Research Agent (Day 03 lab).

Chạy từ starter_v0/:  streamlit run app.py

UI dùng lại nguyên vòng agent của chat.py (run_model_tool_loop), không sửa logic
lõi. Mỗi lượt chat được lưu vào transcripts/ cùng định dạng với chat.py để làm
bằng chứng live chat (REPORT B4).
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import streamlit as st

from chat import (
    ARTIFACTS_DIR,
    ROOT,
    json_text,
    now_iso,
    run_model_tool_loop,
    safe_slug,
    trim_history,
    write_transcript,
)
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version

PROVIDERS = ["gemini", "openrouter", "openai", "anthropic", "ollama"]
SAMPLE_QUESTIONS = [
    "Tin tức AI hôm nay có gì nổi bật?",
    "Tweet mới nhất của Sam Altman là gì?",
    "Tìm 3 paper arXiv mới nộp gần đây nhất về AI agent evaluation.",
    "Tóm tắt bài viết này giúp mình.",
    'Kiểm tra URL và nguồn giúp mình: [{"title":"Paper","url":"https://arxiv.org/abs/1706.03762","source":"arxiv.org"},{"title":"Thiếu nguồn"}]',
    "Đăng bản tin AI hôm nay lên Telegram giúp mình.",
]
TRANSCRIPTS_DIR = ROOT / "transcripts"

st.set_page_config(page_title="Research Agent", page_icon="🔎", layout="wide")


@st.cache_resource(show_spinner=False)
def get_provider(name: str) -> Any:
    return make_provider(name)


def load_artifacts(prompt_path: Path, tools_path: Path) -> tuple[str, list[dict[str, Any]]]:
    system_prompt = prompt_path.read_text(encoding="utf-8")
    tools = to_openai_tools(load_tool_declarations(tools_path))
    return system_prompt, tools


def reset_conversation() -> None:
    st.session_state.messages = []
    st.session_state.history = []
    st.session_state.transcript = None
    st.session_state.transcript_path = None
    st.session_state.config_key = None


def ensure_transcript(config_key: tuple, provider_name: str, model: str | None, version: str,
                      prompt_path: Path, tools_path: Path, history_window: int, max_tool_rounds: int) -> None:
    """Start a new transcript when none exists or the run configuration changed."""
    if st.session_state.transcript is not None and st.session_state.config_key == config_key:
        return
    provider = get_provider(provider_name)
    artifact_version = build_artifact_version(version, prompt_path, tools_path)
    timestamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
    transcript_id = "_".join([safe_slug(version), safe_slug(provider_name), "ui", timestamp])
    st.session_state.transcript = {
        "transcript_id": transcript_id,
        **artifact_version_dict(artifact_version),
        "provider": provider_name,
        "model": model or getattr(provider, "default_model", None),
        "system_prompt": str(prompt_path),
        "tools": str(tools_path),
        "history_window": history_window,
        "max_tool_rounds": max_tool_rounds,
        "interface": "streamlit",
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "turns": [],
    }
    st.session_state.transcript_path = TRANSCRIPTS_DIR / f"{transcript_id}.transcript.json"
    st.session_state.config_key = config_key


def render_rounds(rounds: list[dict[str, Any]]) -> None:
    calls = [call for rnd in rounds for call in rnd.get("tool_calls", [])]
    if not calls:
        st.caption("Không gọi tool.")
        return
    with st.expander(f"🔧 Tool calls ({len(calls)})", expanded=False):
        for rnd in rounds:
            for event in rnd.get("tool_results", []):
                st.markdown(f"**Vòng {rnd['round']} · `{event.get('tool')}`**")
                st.code(json.dumps(event.get("args", {}), ensure_ascii=False, indent=2), language="json")
                st.caption("Kết quả tool")
                st.code(json_text(event.get("result"), max_chars=4000), language="json")


def render_message(msg: dict[str, Any]) -> None:
    with st.chat_message(msg["role"]):
        if msg.get("error"):
            st.error(msg["error"])
        else:
            st.markdown(msg["content"] or "_(không có nội dung)_")
        if msg["role"] == "assistant":
            if msg.get("status") == "waiting_for_user":
                st.info("Agent đang chờ bạn bổ sung thông tin hoặc xác nhận.")
            render_rounds(msg.get("rounds", []))


for key, default in (("messages", []), ("history", []), ("transcript", None),
                     ("transcript_path", None), ("config_key", None)):
    st.session_state.setdefault(key, default)

# ---------------- Sidebar ----------------
with st.sidebar:
    st.header("Cấu hình")
    provider_name = st.selectbox("Provider", PROVIDERS, index=0)
    model = st.text_input("Model", "", help="Để trống để dùng model mặc định của provider.").strip() or None
    version = st.text_input("Version label", "dev", help="Đặt đúng version của prompt đang dùng (vd. v3 khi demo).").strip() or "dev"
    history_window = st.slider("Số cặp hội thoại giữ trong ngữ cảnh", 0, 10, 5)
    max_tool_rounds = st.slider("Số vòng tool tối đa mỗi lượt", 1, 6, 4)
    save_transcript = st.toggle("Lưu transcript vào transcripts/", value=True)
    if st.button("🧹 Cuộc hội thoại mới", use_container_width=True):
        reset_conversation()
        st.rerun()

    prompt_path = ARTIFACTS_DIR / "system_prompt.md"
    tools_path = ARTIFACTS_DIR / "tools.yaml"
    artifact_label = build_artifact_version(version, prompt_path, tools_path).artifact_version
    st.caption(f"Artifact: `{artifact_label}`")
    if st.session_state.transcript_path:
        st.caption(f"Transcript: `{Path(st.session_state.transcript_path).name}`")

    st.subheader("Câu hỏi mẫu")
    for index, sample in enumerate(SAMPLE_QUESTIONS):
        if st.button(sample, key=f"sample_{index}", use_container_width=True):
            st.session_state.pending_prompt = sample

# ---------------- Main ----------------
st.title("🔎 Research Agent")
st.caption(
    "Tìm tin trên web và mạng xã hội, đọc URL, tra paper arXiv, kiểm tra nguồn và định dạng bản tin. "
    "Agent hỏi lại khi thiếu thông tin và chỉ gửi Telegram khi bạn xác nhận."
)

for message in st.session_state.messages:
    render_message(message)

user_text = st.chat_input("Nhập yêu cầu nghiên cứu...") or st.session_state.pop("pending_prompt", None)

if user_text:
    user_text = user_text.strip()
    user_msg = {"role": "user", "content": user_text}
    st.session_state.messages.append(user_msg)
    render_message(user_msg)

    config_key = (provider_name, model, version, history_window, max_tool_rounds)
    ensure_transcript(config_key, provider_name, model, version, prompt_path, tools_path,
                      history_window, max_tool_rounds)
    transcript = st.session_state.transcript
    turn_record: dict[str, Any] = {
        "turn_index": len(transcript["turns"]) + 1,
        "started_at": now_iso(),
        "user": user_text,
        "status": "started",
        "assistant_text": None,
        "rounds": [],
        "tool_events": [],
    }

    system_prompt, openai_tools = load_artifacts(prompt_path, tools_path)
    messages = [
        {"role": "system", "content": system_prompt},
        *trim_history(st.session_state.history, history_window),
        {"role": "user", "content": user_text},
    ]

    with st.spinner("Agent đang xử lý..."):
        try:
            result = run_model_tool_loop(
                provider=get_provider(provider_name),
                messages=messages,
                tools=openai_tools,
                model=model,
                max_tool_rounds=max_tool_rounds,
            )
            turn_record.update(result)
            assistant_msg = {
                "role": "assistant",
                "content": result["assistant_text"],
                "status": result["status"],
                "rounds": result["rounds"],
            }
            st.session_state.history.append({"role": "user", "content": user_text})
            st.session_state.history.append({"role": "assistant", "content": result["assistant_text"]})
        except Exception as exc:  # provider/network errors are shown, not raised
            error = f"{type(exc).__name__}: {exc}"
            turn_record.update({"status": "provider_error", "error": error})
            assistant_msg = {"role": "assistant", "content": "", "error": f"Lỗi provider — {error}", "rounds": []}

    turn_record["ended_at"] = now_iso()
    transcript["turns"].append(turn_record)
    if save_transcript:
        write_transcript(st.session_state.transcript_path, transcript)

    st.session_state.messages.append(assistant_msg)
    render_message(assistant_msg)
