"""Streamlit UI for the Day 03 research agent (CP5).

Run from starter_v0/:

    streamlit run app.py --server.port 8501

This is a thin shell over the same pieces `chat.py` / `run_eval.py` use:
provider -> tool loop -> local tool functions. The UI does not write
transcripts; `chat.py` owns `transcripts/*.transcript.json`.

No API key or secret is rendered: the sidebar only checks whether an env var
is present and shows a warning when a capability is unavailable.
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path
from typing import Any

import streamlit as st

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from chat import run_model_tool_loop, trim_history  # noqa: E402
from env_loader import load_lab_env  # noqa: E402
from providers import make_provider  # noqa: E402
from tools import load_tool_declarations, to_openai_tools  # noqa: E402
from versioning import build_artifact_version  # noqa: E402

load_lab_env(ROOT)

SYSTEM_PROMPT_PATH = ROOT / "artifacts" / "system_prompt.md"
TOOLS_PATH = ROOT / "artifacts" / "tools.yaml"
VERSION = "v3"
HISTORY_WINDOW = 5
MAX_TOOL_ROUNDS = 4

# UI-only: a tool whose env key is missing cannot work, so do not offer it to the
# model. The agent then routes to a source that does work (web / HN / wiki) instead
# of calling a dead tool and surfacing a RuntimeError in the demo.
TOOL_ENV_REQUIREMENTS = {
    "lookup": "TAVILY_API_KEY",
    "fetch": "FIRECRAWL_API_KEY",
    "timeline": "RAPIDAPI_KEY",
    "social_search": "RAPIDAPI_KEY",
}


def split_available_tools(declarations: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[tuple[str, str]]]:
    available: list[dict[str, Any]] = []
    hidden: list[tuple[str, str]] = []
    for item in declarations:
        env_name = TOOL_ENV_REQUIREMENTS.get(item["name"])
        if env_name and not os.getenv(env_name):
            hidden.append((item["name"], env_name))
        else:
            available.append(item)
    return available, hidden


@st.cache_resource
def get_runtime() -> dict[str, Any]:
    provider = make_provider("openrouter")
    declarations = load_tool_declarations(TOOLS_PATH)
    available, hidden = split_available_tools(declarations)
    return {
        "provider": provider,
        "tools": to_openai_tools(available),
        "tool_count": len(available),
        "hidden_tools": hidden,
        "artifact_version": build_artifact_version(VERSION, SYSTEM_PROMPT_PATH, TOOLS_PATH).artifact_version,
        "default_model": getattr(provider, "default_model", None) or "openai/gpt-4o-mini",
    }


def render_sidebar(runtime: dict[str, Any]) -> str | None:
    with st.sidebar:
        st.title("🔎 Research Agent")
        st.caption(f"`{runtime['artifact_version']}`")
        st.caption(f"{runtime['tool_count']} tool đang bật")

        model_text = st.text_input("Model", value=runtime["default_model"])
        model = model_text.strip() or None

        if not os.getenv("OPENROUTER_API_KEY"):
            st.error("Thiếu `OPENROUTER_API_KEY` trong `.env` — model sẽ không trả lời được.")
        for tool_name, env_name in runtime["hidden_tools"]:
            st.warning(f"Đã ẩn `{tool_name}` vì thiếu `{env_name}` — agent sẽ dùng nguồn khác.")
        if not (os.getenv("TELEGRAM_BOT_TOKEN") and os.getenv("TELEGRAM_CHAT_ID")):
            st.info("Chưa cấu hình Telegram → `send` chỉ hỏi xác nhận, không gửi.")

        if st.button("Xoá hội thoại", use_container_width=True):
            st.session_state["messages"] = []
            st.session_state["history"] = []
            st.rerun()

        st.divider()
        st.markdown(
            "**Gợi ý câu hỏi**\n"
            "- Tin AI hôm nay có gì nổi bật?\n"
            "- Trên Hacker News có gì mới về AI agents?\n"
            "- OpenAI là công ty gì?\n"
            "- Đăng bản tin này lên Telegram giúp mình"
        )
    return model


def friendly_error(message: str) -> str:
    """Turn a raw tool error into something a demo viewer can act on."""
    missing = re.search(r"Missing ([A-Z0-9_]+) env var", message or "")
    if missing:
        return f"Thiếu `{missing.group(1)}` trong `.env` — tool này tạm không dùng được."
    return message


def render_tool_events(events: list[dict[str, Any]]) -> None:
    if not events:
        return
    with st.expander(f"🔧 {len(events)} tool call"):
        for event in events:
            st.markdown(f"**`{event.get('tool')}`**")
            st.code(json.dumps(event.get("args") or {}, ensure_ascii=False, indent=2, default=str), language="json")
            result = event.get("result")
            if isinstance(result, dict) and result.get("error"):
                st.error(f"{result['error']}: {friendly_error(result.get('message', ''))}")
            else:
                payload = json.dumps(result, ensure_ascii=False, indent=2, default=str)
                st.code(payload[:4000] + ("\n...<truncated>" if len(payload) > 4000 else ""), language="json")


def main() -> None:
    st.set_page_config(page_title="Research Agent — Day 03", page_icon="🔎", layout="wide")
    runtime = get_runtime()
    model = render_sidebar(runtime)

    st.title("Research Agent")
    st.caption(
        "Hỏi về tin AI, tweet, Hacker News, Wikipedia, paper... "
        "Agent tự chọn tool, chạy thật, rồi trả lời kèm nguồn."
    )

    st.session_state.setdefault("messages", [])
    st.session_state.setdefault("history", [])

    for message in st.session_state["messages"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message["role"] == "assistant":
                render_tool_events(message.get("events") or [])

    prompt = st.chat_input("Nhập yêu cầu research...")
    if not prompt or not prompt.strip():
        return
    prompt = prompt.strip()

    st.session_state["messages"].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    system_prompt = SYSTEM_PROMPT_PATH.read_text(encoding="utf-8")
    messages = [
        {"role": "system", "content": system_prompt},
        *trim_history(st.session_state["history"], HISTORY_WINDOW),
        {"role": "user", "content": prompt},
    ]

    with st.chat_message("assistant"):
        events: list[dict[str, Any]] = []
        with st.spinner("Đang gọi model và tool..."):
            try:
                result = run_model_tool_loop(
                    provider=runtime["provider"],
                    messages=messages,
                    tools=runtime["tools"],
                    model=model,
                    max_tool_rounds=MAX_TOOL_ROUNDS,
                )
                text = result.get("assistant_text") or "(không có nội dung trả về)"
                events = result.get("tool_events") or []
            except Exception as exc:  # provider/network failure: keep the UI usable
                text = f"Lỗi provider: {type(exc).__name__}: {exc}"
                st.error(text)
        st.markdown(text)
        render_tool_events(events)

    st.session_state["messages"].append({"role": "assistant", "content": text, "events": events})
    if not text.startswith("Lỗi provider:"):
        st.session_state["history"] += [
            {"role": "user", "content": prompt},
            {"role": "assistant", "content": text},
        ]


if __name__ == "__main__":
    main()
