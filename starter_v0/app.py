"""Streamlit UI cho Research Agent (Day 03 lab).

Chạy từ starter_v0/:  streamlit run app.py

UI dùng lại nguyên vòng agent của chat.py (run_model_tool_loop), không sửa logic
lõi. Mỗi lượt chat được lưu vào transcripts/ cùng định dạng với chat.py để làm
bằng chứng live chat (REPORT B4).

Quy tắc transcript (để transcript luôn mô tả đúng ngữ cảnh model nhận):
- Prompt/tools được đọc MỘT lần mỗi lượt; hash ghi vào transcript tính từ chính
  bytes gửi cho model, kể cả khi file bị sửa lúc UI đang chạy.
- Đổi provider/model/version/history window/số vòng tool HOẶC đổi nội dung
  prompt/tools giữa hội thoại → bắt đầu hội thoại mới (xóa history + transcript).
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Any

import streamlit as st
import yaml

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
from tools import to_openai_tools
from versioning import ArtifactVersion, artifact_version_dict, build_artifact_version, short_hash

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


def snapshot_artifacts(version: str, prompt_path: Path,
                       tools_path: Path) -> tuple[str, list[dict[str, Any]], ArtifactVersion]:
    """Read prompt/tools once; hash and model input come from the same bytes."""
    prompt_bytes = prompt_path.read_bytes()
    tools_bytes = tools_path.read_bytes()
    prompt_hash = hashlib.sha256(prompt_bytes).hexdigest()  # same as versioning.file_hash
    tools_hash = hashlib.sha256(tools_bytes).hexdigest()
    artifact = ArtifactVersion(
        version=version,
        artifact_version=f"{version}+p{short_hash(prompt_hash)}+t{short_hash(tools_hash)}",
        prompt_hash=prompt_hash,
        tools_hash=tools_hash,
    )
    # Path.read_text() (used by chat.py/run_eval.py) normalizes newlines; do the same.
    system_prompt = prompt_bytes.decode("utf-8").replace("\r\n", "\n").replace("\r", "\n")
    tools = to_openai_tools(yaml.safe_load(tools_bytes.decode("utf-8"))["tools"])
    return system_prompt, tools, artifact


def reset_conversation() -> None:
    st.session_state.messages = []
    st.session_state.history = []
    st.session_state.transcript = None
    st.session_state.transcript_path = None
    st.session_state.config_key = None


def start_transcript(config_key: tuple, provider_name: str, model: str | None, artifact: ArtifactVersion,
                     prompt_path: Path, tools_path: Path, history_window: int, max_tool_rounds: int) -> None:
    provider = get_provider(provider_name)
    timestamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
    transcript_id = "_".join([safe_slug(artifact.version), safe_slug(provider_name), "ui", timestamp])
    st.session_state.transcript = {
        "transcript_id": transcript_id,
        **artifact_version_dict(artifact),
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
    provider_name = st.selectbox("Provider", PROVIDERS, index=0, key="cfg_provider")
    model = st.text_input("Model", "", key="cfg_model",
                          help="Để trống để dùng model mặc định của provider.").strip() or None
    version = st.text_input("Version label", "dev", key="cfg_version",
                            help="Đặt đúng version của prompt đang dùng (vd. v3 khi demo).").strip() or "dev"
    history_window = st.slider("Số cặp hội thoại giữ trong ngữ cảnh", 0, 10, 5, key="cfg_history_window")
    max_tool_rounds = st.slider("Số vòng tool tối đa mỗi lượt", 1, 6, 4, key="cfg_max_tool_rounds")
    save_transcript = st.toggle("Lưu transcript vào transcripts/", value=True)
    if st.button("🧹 Cuộc hội thoại mới", use_container_width=True):
        reset_conversation()
        st.rerun()

    prompt_path = ARTIFACTS_DIR / "system_prompt.md"
    tools_path = ARTIFACTS_DIR / "tools.yaml"
    artifact_label = build_artifact_version(version, prompt_path, tools_path).artifact_version
    st.caption(f"Artifact: `{artifact_label}`")
    st.caption("Đổi cấu hình hoặc prompt/tools giữa chừng sẽ bắt đầu hội thoại mới.")
    if st.session_state.transcript_path and save_transcript:
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

# chat_input is pinned to the bottom of the page, so reading it before rendering is safe.
user_text = st.chat_input("Nhập yêu cầu nghiên cứu...") or st.session_state.pop("pending_prompt", None)
user_text = user_text.strip() if user_text else None

snapshot: tuple[str, list[dict[str, Any]], ArtifactVersion] | None = None
if user_text:
    snapshot = snapshot_artifacts(version, prompt_path, tools_path)
    artifact = snapshot[2]
    config_key = (provider_name, model, version, history_window, max_tool_rounds,
                  artifact.prompt_hash, artifact.tools_hash)
    if st.session_state.transcript is None or st.session_state.config_key != config_key:
        changed_mid_conversation = bool(st.session_state.transcript and st.session_state.transcript["turns"])
        if changed_mid_conversation:
            # Start fresh so the new transcript contains exactly the context the model receives.
            st.session_state.messages = []
            st.session_state.history = []
            st.info("Cấu hình hoặc prompt/tools đã thay đổi — đã bắt đầu hội thoại mới để transcript khớp ngữ cảnh model nhận.")
        start_transcript(config_key, provider_name, model, artifact, prompt_path, tools_path,
                         history_window, max_tool_rounds)

for message in st.session_state.messages:
    render_message(message)

if user_text and snapshot:
    system_prompt, openai_tools, artifact = snapshot
    user_msg = {"role": "user", "content": user_text}
    st.session_state.messages.append(user_msg)
    render_message(user_msg)

    transcript = st.session_state.transcript
    turn_record: dict[str, Any] = {
        "turn_index": len(transcript["turns"]) + 1,
        "started_at": now_iso(),
        "artifact_version": artifact.artifact_version,
        "user": user_text,
        "status": "started",
        "assistant_text": None,
        "rounds": [],
        "tool_events": [],
    }
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
