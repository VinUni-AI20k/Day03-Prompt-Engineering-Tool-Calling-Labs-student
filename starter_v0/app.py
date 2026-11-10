"""Streamlit UI for the Research Agent. Run: streamlit run app.py"""
from __future__ import annotations

import json
from datetime import datetime

import streamlit as st

from chat import (
    ARTIFACTS_DIR, ROOT, now_iso, run_model_tool_loop, trim_history, write_transcript,
)
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version

PROVIDER = "openrouter"
VERSION = "v6"
SYSTEM_PROMPT_PATH = ARTIFACTS_DIR / "system_prompt.md"
TOOLS_PATH = ARTIFACTS_DIR / "tools.yaml"
SAMPLES = [
    "Tin AI hôm nay có gì nổi bật?",
    "Lấy 3 tweet mới nhất của Sam Altman",
    "Trên Hacker News đang bàn gì về Rust?",
    "Tóm tắt bài này: https://openai.com/research/",
    "Đăng bản tin này lên Telegram giúp mình",
]

st.set_page_config(page_title="Research Agent · Nhóm ABC", page_icon="🔎")


@st.cache_resource
def load_agent():
    declarations = load_tool_declarations(TOOLS_PATH)
    provider = make_provider(PROVIDER)
    version = build_artifact_version(VERSION, SYSTEM_PROMPT_PATH, TOOLS_PATH)
    return provider, to_openai_tools(declarations), [d["name"] for d in declarations], version


provider, openai_tools, tool_names, artifact_version = load_agent()
system_prompt = SYSTEM_PROMPT_PATH.read_text(encoding="utf-8")

if "history" not in st.session_state:
    stamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
    st.session_state.history = []
    st.session_state.display = []
    st.session_state.transcript_path = ROOT / "transcripts" / f"{VERSION}_ui_{stamp}.transcript.json"
    st.session_state.transcript = {
        "transcript_id": f"{VERSION}_ui_{stamp}",
        **artifact_version_dict(artifact_version),
        "provider": PROVIDER,
        "model": getattr(provider, "default_model", None),
        "source": "streamlit_ui",
        "created_at": now_iso(),
        "turns": [],
    }

with st.sidebar:
    st.header("Research Agent")
    st.caption(f"artifact: `{artifact_version.artifact_version}`")
    st.markdown("**Tools:** " + ", ".join(f"`{n}`" for n in tool_names))
    st.markdown("**Thử hỏi:**")
    picked = None
    for i, q in enumerate(SAMPLES):
        if st.button(q, key=f"sample_{i}", use_container_width=True):
            picked = q
    if st.button("🧹 Cuộc trò chuyện mới", use_container_width=True):
        st.session_state.clear()
        st.rerun()
    st.markdown("**Lịch sử:**")
    history_files = sorted(
        (ROOT / "transcripts").glob("*.transcript.json"), key=lambda p: p.stat().st_mtime, reverse=True,
    )
    CURRENT = "(phiên hiện tại)"
    viewing = st.selectbox(
        "Xem lại phiên cũ", [CURRENT] + [p.name for p in history_files], label_visibility="collapsed",
    )

st.title("🔎 Research Agent")
st.caption("Tìm tin web, tweet, Hacker News, đọc URL. Hỏi lại khi thiếu thông tin, xin xác nhận trước khi đăng.")


def show_tool_events(events):
    if not events:
        return
    with st.expander(f"🔧 {len(events)} tool call"):
        for ev in events:
            st.markdown(f"**{ev['tool']}** `{json.dumps(ev['args'], ensure_ascii=False)}`")
            st.json(ev.get("result", {}), expanded=False)


if viewing != CURRENT:
    old = json.loads((ROOT / "transcripts" / viewing).read_text(encoding="utf-8"))
    st.info(f"Đang xem lại `{viewing}` · {len(old.get('turns', []))} lượt. Chọn **{CURRENT}** để chat tiếp.")
    for t in old.get("turns", []):
        with st.chat_message("user"):
            st.markdown(t.get("user", ""))
        with st.chat_message("assistant"):
            st.markdown(t.get("assistant_text") or t.get("error") or "(không có trả lời)")
            show_tool_events(t.get("tool_events"))
    st.stop()

for msg in st.session_state.display:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        show_tool_events(msg.get("tool_events"))

user_text = st.chat_input("Hỏi agent...") or picked
if user_text:
    st.session_state.display.append({"role": "user", "content": user_text})
    with st.chat_message("user"):
        st.markdown(user_text)

    messages = [
        {"role": "system", "content": system_prompt},
        *trim_history(st.session_state.history, 5),
        {"role": "user", "content": user_text},
    ]
    turn = {"turn_index": len(st.session_state.transcript["turns"]) + 1, "started_at": now_iso(), "user": user_text}
    with st.chat_message("assistant"):
        with st.spinner("Đang xử lý..."):
            try:
                result = run_model_tool_loop(
                    provider=provider, messages=messages, tools=openai_tools, model=None, max_tool_rounds=4,
                )
                answer = result["assistant_text"] or "(không có trả lời)"
                turn.update(result)
            except Exception as exc:
                answer = f"⚠️ Lỗi: {type(exc).__name__}: {exc}"
                result = {"tool_events": []}
                turn.update({"status": "provider_error", "error": answer})
        st.markdown(answer)
        show_tool_events(result.get("tool_events"))

    st.session_state.history += [{"role": "user", "content": user_text}, {"role": "assistant", "content": answer}]
    st.session_state.display.append({"role": "assistant", "content": answer, "tool_events": result.get("tool_events")})
    turn["ended_at"] = now_iso()
    st.session_state.transcript["turns"].append(turn)
    st.session_state.transcript["updated_at"] = now_iso()
    write_transcript(st.session_state.transcript_path, st.session_state.transcript)
