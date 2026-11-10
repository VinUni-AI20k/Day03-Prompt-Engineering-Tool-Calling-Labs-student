from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any

import streamlit as st

from chat import now_iso, run_model_tool_loop, safe_slug, trim_history, write_transcript
from env_loader import load_lab_env
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version

ROOT = Path(__file__).resolve().parent
ARTIFACTS_DIR = ROOT / "artifacts"
TRANSCRIPTS_DIR = ROOT / "transcripts"
SYSTEM_PROMPT_PATH = ARTIFACTS_DIR / "system_prompt.md"
TOOLS_YAML_PATH = ARTIFACTS_DIR / "tools.yaml"

load_lab_env(ROOT)

PROVIDER_ENV_MAP = {
    "openrouter": "OPENROUTER_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
    "openai": "OPENAI_API_KEY",
    "gemini": "GEMINI_API_KEY",
    "ollama": None,
}

TOOL_ENV_VARS = [
    "TAVILY_API_KEY",
    "FIRECRAWL_API_KEY",
    "RAPIDAPI_KEY",
    "TELEGRAM_BOT_TOKEN",
    "TELEGRAM_CHAT_ID",
]

SAMPLE_PROMPTS = [
    ("Tin tức AI hôm nay (lookup)", "Tìm 3 tin tức mới nhất hôm nay về AI agents trên web."),
    ("Thiếu thông tin (clarify)", "Tóm tắt các tweet mới nhất giúp mình."),
    ("Tìm repo GitHub (github_repos)", "Tìm 3 repo GitHub Python về AI agent đang hot tuần này."),
    ("Kiểm tra PyPI (pypi_package)", "Kiểm tra phiên bản mới nhất và license của thư viện fastapi trên PyPI."),
    ("Tìm model Hugging Face (hf_models)", "Tìm 3 model open-weights nhẹ về embedding trên Hugging Face."),
    ("Gửi Telegram (clarify yes_no)", "Đăng bản tin tóm tắt AI vừa rồi lên Telegram nhé."),
]


def _default_provider_index() -> int:
    providers = list(PROVIDER_ENV_MAP)
    for idx, name in enumerate(providers):
        env_var = PROVIDER_ENV_MAP[name]
        if env_var and os.getenv(env_var, "").strip():
            return idx
    return 0


def _load_artifacts() -> tuple[str, list[dict[str, Any]], list[dict[str, Any]]]:
    system_prompt = SYSTEM_PROMPT_PATH.read_text(encoding="utf-8")
    declarations = load_tool_declarations(TOOLS_YAML_PATH)
    return system_prompt, declarations, to_openai_tools(declarations)


def _new_transcript(
    *,
    version_label: str,
    provider_name: str,
    model_name: str | None,
    history_window: int,
    max_tool_rounds: int,
) -> tuple[Path, dict[str, Any]]:
    artifact_version = build_artifact_version(version_label, SYSTEM_PROMPT_PATH, TOOLS_YAML_PATH)
    timestamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
    transcript_id = f"ui_{safe_slug(version_label)}_{safe_slug(provider_name)}_{timestamp}"
    path = TRANSCRIPTS_DIR / f"{transcript_id}.transcript.json"
    data: dict[str, Any] = {
        "transcript_id": transcript_id,
        **artifact_version_dict(artifact_version),
        "provider": provider_name,
        "model": model_name,
        "system_prompt": str(SYSTEM_PROMPT_PATH),
        "tools": str(TOOLS_YAML_PATH),
        "history_window": history_window,
        "max_tool_rounds": max_tool_rounds,
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "turns": [],
    }
    return path, data


def _extract_clarify_prompt(tool_events: list[dict[str, Any]]) -> dict[str, Any] | None:
    for event in reversed(tool_events):
        result = event.get("result")
        if isinstance(result, dict) and result.get("awaiting_user"):
            return result
    return None


def _has_tool_error(tool_events: list[dict[str, Any]]) -> bool:
    for event in tool_events:
        res = event.get("result")
        if event.get("error") or (isinstance(res, dict) and res.get("error")):
            return True
    return False


def _render_tool_trace(turn: dict[str, Any]) -> None:
    tool_events = turn.get("tool_events") or []
    status = turn.get("status", "")
    provider_error = turn.get("error")

    if provider_error:
        st.error(f"Provider error: {provider_error}")

    if not tool_events and status == "answered":
        return

    has_err = bool(provider_error) or _has_tool_error(tool_events)
    label = f"Tool trace ({len(tool_events)} call(s)) · status: {status}"
    with st.expander(label, expanded=has_err):
        for idx, event in enumerate(tool_events, start=1):
            name = event.get("tool", "unknown")
            args = event.get("args", {})
            st.markdown(f"**{idx}. `{name}`**")
            st.code(json.dumps(args, ensure_ascii=False, indent=2), language="json")
            res = event.get("result")
            if event.get("error") or (isinstance(res, dict) and res.get("error")):
                st.error(f"Tool `{name}` returned error")
            st.json(res if res is not None else event)


def _init_session_state(
    version_label: str,
    provider_name: str,
    model_name: str | None,
    history_window: int,
    max_tool_rounds: int,
) -> None:
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "history" not in st.session_state:
        st.session_state.history = []
    if "transcript_path" not in st.session_state or "transcript" not in st.session_state:
        path, data = _new_transcript(
            version_label=version_label,
            provider_name=provider_name,
            model_name=model_name,
            history_window=history_window,
            max_tool_rounds=max_tool_rounds,
        )
        st.session_state.transcript_path = path
        st.session_state.transcript = data
    if "pending_prompt" not in st.session_state:
        st.session_state.pending_prompt = None


def _reset_chat(
    version_label: str,
    provider_name: str,
    model_name: str | None,
    history_window: int,
    max_tool_rounds: int,
) -> None:
    st.session_state.messages = []
    st.session_state.history = []
    path, data = _new_transcript(
        version_label=version_label,
        provider_name=provider_name,
        model_name=model_name,
        history_window=history_window,
        max_tool_rounds=max_tool_rounds,
    )
    st.session_state.transcript_path = path
    st.session_state.transcript = data
    st.session_state.pending_prompt = None


def _process_user_turn(
    user_text: str,
    *,
    system_prompt: str,
    openai_tools: list[dict[str, Any]],
    provider_name: str,
    model_override: str,
    history_window: int,
    max_tool_rounds: int,
) -> None:
    model_arg = model_override.strip() or None
    transcript: dict[str, Any] = st.session_state.transcript
    turn_index = len(transcript["turns"]) + 1

    st.session_state.messages.append({"role": "user", "content": user_text})
    with st.chat_message("user"):
        st.markdown(user_text)

    messages = [
        {"role": "system", "content": system_prompt},
        *trim_history(st.session_state.history, history_window),
        {"role": "user", "content": user_text},
    ]
    turn_record: dict[str, Any] = {
        "turn_index": turn_index,
        "started_at": now_iso(),
        "user": user_text,
        "status": "started",
        "assistant_text": None,
        "rounds": [],
        "tool_events": [],
    }

    with st.chat_message("assistant"):
        with st.spinner("Đang chạy Research Agent..."):
            try:
                provider = make_provider(provider_name)
                transcript["provider"] = provider_name
                transcript["model"] = model_arg or getattr(provider, "default_model", None)
                result = run_model_tool_loop(
                    provider=provider,
                    messages=messages,
                    tools=openai_tools,
                    model=model_arg,
                    max_tool_rounds=max_tool_rounds,
                )
                turn_record.update(result)
                assistant_text = result["assistant_text"] or ""
                st.markdown(assistant_text)
                _render_tool_trace(turn_record)
                st.session_state.history.append({"role": "user", "content": user_text})
                st.session_state.history.append({"role": "assistant", "content": assistant_text})
            except Exception as exc:
                err_msg = f"{type(exc).__name__}: {exc}"
                turn_record.update({"status": "provider_error", "error": err_msg, "assistant_text": err_msg})
                st.error(err_msg)

        turn_record["ended_at"] = now_iso()
        transcript["turns"].append(turn_record)
        write_transcript(st.session_state.transcript_path, transcript)
        st.session_state.messages.append({
            "role": "assistant",
            "content": turn_record.get("assistant_text") or "",
            "turn": turn_record,
        })


def main() -> None:
    st.set_page_config(page_title="Day 03 Research Agent", page_icon="🔎", layout="wide")
    st.title("🔎 Research Agent — Tool Calling UI")
    st.caption("Hiển thị minh bạch tool calls, arguments, kết quả & lỗi thật từ tool/provider.")

    system_prompt, declarations, openai_tools = _load_artifacts()

    with st.sidebar:
        st.header("Cấu hình Agent")
        providers = list(PROVIDER_ENV_MAP)
        provider_name = st.selectbox("Provider", providers, index=_default_provider_index())
        model_override = st.text_input("Model override (để trống dùng mặc định)", value="")
        version_label = st.text_input("Artifact version label", value="v6")
        history_window = st.slider("History window (turns)", min_value=1, max_value=10, value=5)
        max_tool_rounds = st.slider("Max tool rounds / turn", min_value=1, max_value=8, value=4)

        artifact_version = build_artifact_version(version_label, SYSTEM_PROMPT_PATH, TOOLS_YAML_PATH)
        st.code(artifact_version.artifact_version, language="text")

        _init_session_state(
            version_label=version_label,
            provider_name=provider_name,
            model_name=model_override.strip() or None,
            history_window=history_window,
            max_tool_rounds=max_tool_rounds,
        )

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Cuộc chat mới", use_container_width=True):
                _reset_chat(
                    version_label=version_label,
                    provider_name=provider_name,
                    model_name=model_override.strip() or None,
                    history_window=history_window,
                    max_tool_rounds=max_tool_rounds,
                )
                st.rerun()
        with col2:
            transcript_json = json.dumps(st.session_state.transcript, ensure_ascii=False, indent=2, default=str)
            st.download_button(
                "Tải transcript",
                data=transcript_json,
                file_name=st.session_state.transcript_path.name,
                mime="application/json",
                use_container_width=True,
            )

        st.divider()
        st.subheader("Câu hỏi mẫu")
        for label, prompt_text in SAMPLE_PROMPTS:
            if st.button(label, key=f"sample_{label}", use_container_width=True):
                st.session_state.pending_prompt = prompt_text

        st.divider()
        with st.expander(f"Tools đang khai báo ({len(declarations)})"):
            for item in declarations:
                st.markdown(f"- **`{item['name']}`**")

        with st.expander("Trạng thái API Keys (.env)"):
            needed = [v for v in PROVIDER_ENV_MAP.values() if v] + TOOL_ENV_VARS
            for env_name in needed:
                ok = bool(os.getenv(env_name, "").strip())
                st.markdown(f"- `{'✅' if ok else '⚪'}` `{env_name}`")

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg["role"] == "assistant" and "turn" in msg:
                _render_tool_trace(msg["turn"])

    # Quick-reply buttons when the agent paused via `clarify` (yes_no or choice)
    if st.session_state.messages and st.session_state.messages[-1]["role"] == "assistant":
        last_turn = st.session_state.messages[-1].get("turn", {})
        if last_turn.get("status") == "waiting_for_user":
            clarify_info = _extract_clarify_prompt(last_turn.get("tool_events", []))
            if clarify_info:
                rtype = clarify_info.get("response_type")
                if rtype == "yes_no":
                    c1, c2 = st.columns([1, 5])
                    with c1:
                        if st.button("Đồng ý gửi", type="primary"):
                            st.session_state.pending_prompt = "Đồng ý, hãy gửi đi."
                    with c2:
                        if st.button("Hủy, không gửi"):
                            st.session_state.pending_prompt = "Không, hủy giúp mình."
                elif rtype == "choice" and clarify_info.get("options"):
                    cols = st.columns(min(len(clarify_info["options"]), 4))
                    for i, opt in enumerate(clarify_info["options"][:4]):
                        if cols[i].button(str(opt), key=f"opt_{len(st.session_state.messages)}_{i}"):
                            st.session_state.pending_prompt = str(opt)

    chat_input = st.chat_input("Nhập câu hỏi nghiên cứu, URL, arXiv ID, hoặc yêu cầu gửi Telegram...")
    prompt_to_run = st.session_state.pending_prompt or chat_input
    if prompt_to_run:
        st.session_state.pending_prompt = None
        _process_user_turn(
            prompt_to_run,
            system_prompt=system_prompt,
            openai_tools=openai_tools,
            provider_name=provider_name,
            model_override=model_override,
            history_window=history_window,
            max_tool_rounds=max_tool_rounds,
        )
        st.rerun()


if __name__ == "__main__":
    main()

