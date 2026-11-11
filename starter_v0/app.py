"""Streamlit UI for the Research Agent (Claude Code style).

Run from `starter_v0/`:
    streamlit run app.py

Reuses the exact tool loop of `chat.py` (same prompt, tools, clarify pause) and
writes the same transcript format to `transcripts/ui_*.transcript.json`, so UI
sessions are valid live-chat evidence. Tool errors are shown, never hidden.

Layout: sidebar = suggested prompts + tool list only; configuration lives in a
popover at the top of the main area.
"""
from __future__ import annotations

import csv
import html
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any

import streamlit as st

from chat import (
    ARTIFACTS_DIR,
    ROOT,
    now_iso,
    run_model_tool_loop,
    safe_slug,
    trim_history,
    write_transcript,
)
from providers import make_provider
from tools import TOOL_FUNCTIONS, load_tool_declarations, to_openai_tools
from tools.send.tool import _is_confirmed, send_telegram
from versioning import artifact_version_dict, build_artifact_version

PROVIDERS = ["openrouter", "openai", "anthropic", "gemini", "ollama"]
# Provider/model for the UI — same as the eval runs from v5 on: local Ollama model
# qwen2.5-7b-lab (qwen2.5:7b, see artifacts/local/Modelfile.qwen2.5-7b-lab). Override with AGENT_PROVIDER / AGENT_MODEL.
DEFAULT_PROVIDER = os.getenv("AGENT_PROVIDER", "ollama")
DEFAULT_MODEL = os.getenv("AGENT_MODEL", "qwen2.5-7b-lab")
VERSION_LOG_PATH = ARTIFACTS_DIR / "version_log.csv"
SYSTEM_PROMPT_PATH = ARTIFACTS_DIR / "system_prompt.md"
# Demo các version: prompt cũ lưu trong artifacts/versions; mục đầu = system_prompt.md đang chạy (v7).
# v2 không còn bản prompt trong git, chỉ có hash + số liệu trong version_log.csv.
PROMPT_CHOICES = {
    "hiện tại (v7)": SYSTEM_PROMPT_PATH,
    "v4 — routing + tools.yaml (prompt v3)": ARTIFACTS_DIR / "versions" / "v3_system_prompt.md",
    "v1 — cho phép hỏi lại, vẫn gửi ngay": ARTIFACTS_DIR / "versions" / "v1_system_prompt.md",
    "v0 — baseline: không hỏi lại, gửi ngay": ARTIFACTS_DIR / "versions" / "v0_system_prompt.md",
}
TOOLS_PATH = ARTIFACTS_DIR / "tools.yaml"
TRANSCRIPTS_DIR = ROOT / "transcripts"

EXAMPLES = [
    "Tin tức mới nhất về AI agent trong tuần này?",
    "Sam Altman gần đây đăng gì trên X?",
    "Mọi người trên X đang nói gì nổi bật về GPT-5?",
    "Tìm paper trên arXiv về mixture of experts",
    "Repo psf/requests có bao nhiêu sao?",
    "Theo policy nội bộ, trích dẫn nguồn cần ghi gì?",
    "Tóm tắt giúp tôi bài viết này",
    "Gửi bản tin vừa tổng hợp lên Telegram",
]

CSS = """
<style>
html, body, [class*="st-"], .stMarkdown, button, input, textarea {
  font-family: 'JetBrains Mono','Cascadia Code',Consolas,monospace !important;
}
/* Giữ font icon (Material Symbols dùng ligature): nếu bị ép monospace sẽ hiện chữ "expand_more", "arrow_right" đè lên nhau */
[data-testid="stIconMaterial"], span[class*="material-symbols"], span[class*="material-icons"] {
  font-family: 'Material Symbols Rounded','Material Symbols Outlined','Material Icons' !important;
}
header[data-testid="stHeader"] { background: transparent; }
.block-container { max-width: 62rem; padding-top: 2rem; }
.cc-banner { border: 1px solid #d97757; border-radius: 6px; padding: .7rem 1rem; color:#e8e6e3; }
.cc-banner b { color:#d97757; }
.cc-banner small { color:#9a968f; display:block; margin-top:.2rem; }
.cc-user { color:#9a968f; background:#2b2a28; border-radius:4px; padding:.45rem .8rem; margin:1rem 0 .4rem; white-space:pre-wrap; }
.cc-user::before { content:"> "; color:#d97757; font-weight:700; }
.cc-msg { margin:.4rem 0; padding-left:1.4rem; text-indent:-1.4rem; white-space:pre-wrap; }
.cc-msg::before { content:"● "; color:#e8e6e3; }
.cc-tool { margin:.5rem 0 .1rem; }
.cc-tool::before { content:"● "; color:#4ec27a; }
.cc-tool.err::before { color:#e5534b; }
.cc-tool b { color:#e8e6e3; }
.cc-tool span { color:#9a968f; }
.cc-res { color:#9a968f; padding-left:1.4rem; margin-bottom:.2rem; }
.cc-res::before { content:"⎿  "; }
.cc-hint { color:#9a968f; font-size:.8rem; }
section[data-testid="stSidebar"] { border-right:1px solid #33322f; }
section[data-testid="stSidebar"] .stButton button {
  text-align:left; justify-content:flex-start; font-size:.78rem; padding:.3rem .6rem;
  border-color:#33322f; background:transparent;
}
section[data-testid="stSidebar"] .stButton button:hover { border-color:#d97757; color:#d97757; }
div[data-testid="stChatInput"] { border:1px solid #d97757; border-radius:6px; }
</style>
"""

st.set_page_config(page_title="Research Agent — NhomSNN", page_icon="🔎", layout="wide")
st.markdown(CSS, unsafe_allow_html=True)


# ---------------------------------------------------------------- helpers
def detect_version_label(prompt_path: Path = SYSTEM_PROMPT_PATH) -> str:
    """Return the version_log label whose prompt+tools hashes match the current files.

    Prevents transcripts labelled e.g. "v3" while the starter prompt is still running.
    """
    current = build_artifact_version("probe", prompt_path, TOOLS_PATH)
    try:
        with VERSION_LOG_PATH.open(encoding="utf-8") as fh:
            rows = list(csv.DictReader(fh))
    except OSError:
        rows = []
    for row in reversed(rows):
        if (row.get("prompt_hash") or "").strip() == current.prompt_hash and (
            row.get("tools_hash") or ""
        ).strip() == current.tools_hash:
            return (row.get("version") or "").strip() or "unversioned"
    return "unversioned"


def new_transcript(provider_name: str, model: str | None, version: str, history_window: int, max_rounds: int, prompt_path: Path) -> dict[str, Any]:
    artifact_version = build_artifact_version(version, prompt_path, TOOLS_PATH)
    timestamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
    transcript_id = "_".join(["ui", safe_slug(version), safe_slug(provider_name), timestamp])
    return {
        "transcript_id": transcript_id,
        **artifact_version_dict(artifact_version),
        "provider": provider_name,
        "model": model,
        "system_prompt": str(prompt_path),
        "tools": str(TOOLS_PATH),
        "history_window": history_window,
        "max_tool_rounds": max_rounds,
        "interface": "streamlit",
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "turns": [],
    }


def reset_session(config: tuple) -> None:
    provider_name, model, version, history_window, max_rounds, prompt_choice = config
    st.session_state.config = config
    st.session_state.history = []
    st.session_state.pending_send = None
    st.session_state.transcript = new_transcript(provider_name, model, version, history_window, max_rounds, PROMPT_CHOICES[prompt_choice])
    st.session_state.transcript_path = TRANSCRIPTS_DIR / f"{st.session_state.transcript['transcript_id']}.transcript.json"


def result_has_error(result: Any) -> bool:
    return isinstance(result, dict) and bool(result.get("error"))


def _short(value: Any, limit: int = 90) -> str:
    text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, default=str)
    return text if len(text) <= limit else text[: limit - 1] + "…"


def _args_line(args: Any) -> str:
    if not isinstance(args, dict):
        return _short(args)
    return ", ".join(f"{k}={_short(v, 40)}" for k, v in args.items())


def _result_line(result: Any) -> str:
    if not isinstance(result, dict):
        return _short(result)
    if result.get("error"):
        return f"{result.get('error')}: {_short(result.get('message', ''), 120)}"
    if isinstance(result.get("items"), list):
        return f"{len(result['items'])} item"
    if isinstance(result.get("results"), list):
        return f"{len(result['results'])} kết quả"
    if result.get("status"):
        return str(result["status"])
    return _short(result)


def render_turn_details(turn: dict[str, Any]) -> None:
    """Claude Code style: `● tool(args)` + `⎿ summary` per call; raw JSON in an expander."""
    status = turn.get("status")
    if status == "provider_error":
        st.error(f"Provider error: {turn.get('error')}")
        return
    if status == "waiting_for_user":
        st.markdown('<div class="cc-hint">⏸ Agent đang chờ bạn trả lời câu hỏi trên (clarify).</div>', unsafe_allow_html=True)
    elif status == "max_tool_rounds":
        st.warning("Agent dừng vì chạm giới hạn số vòng gọi tool.")

    for event in turn.get("tool_events") or []:
        failed = result_has_error(event.get("result"))
        st.markdown(
            f'<div class="cc-tool{" err" if failed else ""}"><b>{html.escape(str(event.get("tool")))}</b>'
            f'<span>({html.escape(_args_line(event.get("args")))})</span></div>'
            f'<div class="cc-res">{html.escape(_result_line(event.get("result")))}</div>',
            unsafe_allow_html=True,
        )
        with st.expander("chi tiết", expanded=False):
            st.json({"args": event.get("args"), "result": event.get("result")}, expanded=False)


def _gated_send(text: str = "", confirmed: Any = False) -> dict[str, Any]:
    """Human-in-the-loop gate: the model can never reach Telegram directly from the UI.

    Unconfirmed calls behave as before; a confirmed call is parked until the user presses
    Approve/Reject (see `render_send_approval`).
    """
    if not _is_confirmed(confirmed):
        return send_telegram(text=text, confirmed=confirmed)
    st.session_state.pending_send = {"text": text}
    return {
        "tool": "send_telegram",
        "status": "pending_user_approval",
        "message": "Đã hiện nút Đồng ý/Từ chối cho người dùng. Chưa gửi. Không gọi lại send và không nói là đã gửi.",
    }


def _record_send_event(result: dict[str, Any], text: str, decision: str) -> None:
    transcript = st.session_state.transcript
    if transcript["turns"]:
        transcript["turns"][-1].setdefault("tool_events", []).append({
            "tool": "send",
            "args": {"text": text, "confirmed": decision == "approved", "decided_by": "ui_button"},
            "result": result,
        })
    st.session_state.history.append({
        "role": "assistant",
        "content": f"[Hệ thống] Người dùng đã {'bấm Đồng ý' if decision == 'approved' else 'bấm Từ chối'}. "
                   f"Kết quả send: {result.get('status') or result.get('error')}.",
    })
    write_transcript(st.session_state.transcript_path, transcript)


def render_send_approval() -> None:
    pending = st.session_state.get("pending_send")
    if not pending:
        return
    st.markdown(
        '<div class="cc-banner"><b>⚠ Xác nhận gửi lên Telegram</b>'
        "<small>Hành động ra bên ngoài, không thu hồi được. Nội dung sẽ gửi:</small></div>",
        unsafe_allow_html=True,
    )
    st.code(pending["text"], language="markdown")
    ok, no = st.columns(2)
    if ok.button("✅ Đồng ý gửi", key="send_ok", use_container_width=True, type="primary"):
        result = send_telegram(text=pending["text"], confirmed=True)
        _record_send_event(result, pending["text"], "approved")
        st.session_state.pending_send = None
        st.rerun()
    if no.button("✖ Từ chối", key="send_no", use_container_width=True):
        _record_send_event({"tool": "send_telegram", "status": "rejected"}, pending["text"], "rejected")
        st.session_state.pending_send = None
        st.rerun()


def run_turn(user_text: str) -> None:
    provider_name, model, _version, history_window, max_rounds, prompt_choice = st.session_state.config
    transcript = st.session_state.transcript
    system_prompt = PROMPT_CHOICES[prompt_choice].read_text(encoding="utf-8")
    openai_tools = to_openai_tools(load_tool_declarations(TOOLS_PATH))

    messages = [
        {"role": "system", "content": system_prompt},
        *trim_history(st.session_state.history, history_window),
        {"role": "user", "content": user_text},
    ]
    turn: dict[str, Any] = {
        "turn_index": len(transcript["turns"]) + 1,
        "started_at": now_iso(),
        "user": user_text,
        "status": "started",
        "assistant_text": None,
        "rounds": [],
        "tool_events": [],
    }
    original_send = TOOL_FUNCTIONS["send"]
    TOOL_FUNCTIONS["send"] = _gated_send
    try:
        provider = make_provider(provider_name)
        result = run_model_tool_loop(
            provider=provider,
            messages=messages,
            tools=openai_tools,
            model=model,
            max_tool_rounds=max_rounds,
        )
        turn.update(result)
        st.session_state.history.append({"role": "user", "content": user_text})
        st.session_state.history.append({"role": "assistant", "content": result["assistant_text"]})
    except Exception as exc:  # show provider problems instead of hiding them
        turn.update({"status": "provider_error", "error": f"{type(exc).__name__}: {exc}"})
    finally:
        TOOL_FUNCTIONS["send"] = original_send

    turn["ended_at"] = now_iso()
    transcript["turns"].append(turn)
    write_transcript(st.session_state.transcript_path, transcript)


# ---------------------------------------------------------------- sidebar: suggestions + tools only
with st.sidebar:
    st.markdown("##### Gợi ý")
    for i, example in enumerate(EXAMPLES):
        if st.button(example, key=f"ex{i}", use_container_width=True):
            st.session_state.pending = example

    st.markdown("##### Công cụ")
    try:
        for decl in load_tool_declarations(TOOLS_PATH):
            desc = " ".join(str(decl.get("description", "")).split())
            with st.expander(decl["name"]):
                st.caption(desc)
    except Exception as exc:
        st.error(f"Không đọc được tools.yaml: {exc}")


# ---------------------------------------------------------------- header + config popover
head, cfg = st.columns([5, 1])
with head:
    st.markdown(
        '<div class="cc-banner"><b>✻ Research Agent</b> — NhomSNN'
        "<small>Tìm tin theo từ khóa / tài khoản X, tìm web, đọc URL, tổng hợp digest. "
        "Hỏi lại khi thiếu thông tin và xin xác nhận trước khi gửi Telegram.</small></div>",
        unsafe_allow_html=True,
    )
with cfg:
    with st.popover("⚙ Cấu hình", use_container_width=True):
        provider_name = st.selectbox(
            "Provider", PROVIDERS, index=PROVIDERS.index(DEFAULT_PROVIDER) if DEFAULT_PROVIDER in PROVIDERS else 0
        )
        model = st.text_input("Model (để trống = mặc định của provider)", value=DEFAULT_MODEL).strip() or None
        prompt_choice = st.selectbox("Prompt version (demo so sánh)", list(PROMPT_CHOICES))
        detected_version = detect_version_label(PROMPT_CHOICES[prompt_choice])
        if prompt_choice != next(iter(PROMPT_CHOICES)):
            detected_version = prompt_choice.split(" ")[0]
        version = st.text_input(
            "Version label (tự nhận theo hash trong version_log.csv)", value=detected_version
        ).strip() or detected_version
        if detected_version == "unversioned":
            st.warning("Prompt/tools hiện tại chưa khớp version nào trong version_log.csv.")
        history_window = st.slider("History window (cặp lượt)", 0, 10, 5)
        max_rounds = st.slider("Max tool rounds", 1, 8, 4)
        config = (provider_name, model, version, history_window, max_rounds, prompt_choice)

        if "config" not in st.session_state:
            reset_session(config)
        new_chat = st.button("🔄 Cuộc trò chuyện mới", use_container_width=True)
        if new_chat or st.session_state.config != config:
            reset_session(config)

        t = st.session_state.transcript
        st.caption("Artifact đang chạy")
        st.code(
            f"artifact_version: {t.get('artifact_version')}\n"
            f"prompt_hash: {t.get('prompt_hash')}\n"
            f"tools_hash: {t.get('tools_hash')}",
            language="text",
        )
        st.caption("Transcript")
        st.code(str(st.session_state.transcript_path.relative_to(ROOT)), language="text")


# ---------------------------------------------------------------- main
for turn in st.session_state.transcript["turns"]:
    st.markdown(f'<div class="cc-user">{html.escape(turn["user"])}</div>', unsafe_allow_html=True)
    if turn.get("assistant_text"):
        st.markdown(f'<div class="cc-msg">{html.escape(turn["assistant_text"])}</div>', unsafe_allow_html=True)
    render_turn_details(turn)

render_send_approval()

user_text = st.chat_input("Nhập yêu cầu research…") or st.session_state.pop("pending", None)
if user_text:
    st.markdown(f'<div class="cc-user">{html.escape(user_text)}</div>', unsafe_allow_html=True)
    with st.spinner("✻ Agent đang chọn tool và chạy…"):
        run_turn(user_text)
    st.rerun()
