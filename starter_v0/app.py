from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

import streamlit as st

from chat import now_iso, run_model_tool_loop, safe_slug, trim_history, write_transcript
from env_loader import load_lab_env
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version


ROOT = Path(__file__).parent
ARTIFACTS_DIR = ROOT / "artifacts"
TRANSCRIPTS_DIR = ROOT / "transcripts"
SYSTEM_PROMPT_PATH = ARTIFACTS_DIR / "system_prompt.md"
TOOLS_PATH = ARTIFACTS_DIR / "tools.yaml"
VERSION = "v3"
HISTORY_WINDOW = 5
MAX_TOOL_ROUNDS = 4
PROVIDERS = ["openrouter", "openai", "anthropic", "gemini", "ollama"]

load_lab_env(ROOT)
st.set_page_config(page_title="Research Agent", page_icon="R", layout="centered")

st.markdown(
    """
    <style>
      :root { --ink:#172b3a; --muted:#718096; --line:#e7edf1; --accent:#167d79; }
      html, body, [class*="css"] { font-family:Inter,system-ui,sans-serif; }
      .stApp { background:#f7f9fa; color:var(--ink); }
      [data-testid="stHeader"] { background:transparent; }
      [data-testid="stMain"] .block-container { max-width:820px; padding-top:2.1rem; padding-bottom:7rem; }
      .agent-topline { display:flex; align-items:center; gap:.65rem; margin-bottom:1.4rem; }
      .agent-mark { width:2.2rem; height:2.2rem; border-radius:.75rem; display:grid; place-items:center; color:white; background:var(--accent); font-size:1.3rem; }
      .agent-name { font-size:1.12rem; font-weight:700; letter-spacing:-.035em; }
      [data-testid="stChatMessage"] { border:1px solid var(--line); border-radius:16px; padding:.85rem 1rem; background:white; box-shadow:0 3px 14px rgba(24,45,60,.035); }
      [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] p { line-height:1.65; }
      [data-testid="stChatInput"] { border-color:#dce5e8; border-radius:16px; box-shadow:0 8px 30px rgba(24,45,60,.08); }
      [data-testid="stChatInput"]:focus-within { border-color:var(--accent); box-shadow:0 0 0 1px var(--accent),0 8px 30px rgba(24,45,60,.08); }
      [data-testid="stSidebar"] { background:white; border-right:1px solid var(--line); }
      [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h2 { font-size:1rem; letter-spacing:-.02em; }
      [data-testid="stExpander"] { border:1px solid var(--line); border-radius:12px; background:white; }
      .stButton button, .stDownloadButton button { border-radius:10px; font-weight:600; }
      #MainMenu, footer { visibility:hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)


def start_conversation(provider_name: str, model_override: str | None) -> None:
    provider = make_provider(provider_name)
    selected_model = model_override or getattr(provider, "default_model", None)
    artifact_version = build_artifact_version(VERSION, SYSTEM_PROMPT_PATH, TOOLS_PATH)
    timestamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
    transcript_id = "_".join([VERSION, safe_slug(provider_name), "streamlit", timestamp])
    transcript_path = TRANSCRIPTS_DIR / f"{transcript_id}.transcript.json"

    st.session_state["settings"] = {
        "provider": provider_name,
        "model": model_override,
        "selected_model": selected_model,
    }
    st.session_state["history"] = []
    st.session_state["messages"] = []
    st.session_state["transcript_path"] = str(transcript_path)
    st.session_state["transcript"] = {
        "transcript_id": transcript_id,
        **artifact_version_dict(artifact_version),
        "provider": provider_name,
        "model": selected_model,
        "system_prompt": str(SYSTEM_PROMPT_PATH),
        "tools": str(TOOLS_PATH),
        "ui": "streamlit",
        "history_window": HISTORY_WINDOW,
        "max_tool_rounds": MAX_TOOL_ROUNDS,
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "turns": [],
    }
    write_transcript(transcript_path, st.session_state["transcript"])


def render_messages() -> None:
    for message in st.session_state["messages"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            events = message.get("tool_events", [])
            if events:
                with st.expander("Sources and tools"):
                    for event in events:
                        st.json(event)


def handle_user_turn(user_text: str) -> None:
    history = st.session_state["history"]
    settings = st.session_state["settings"]
    provider = make_provider(settings["provider"])
    declarations = load_tool_declarations(TOOLS_PATH)
    tool_schemas = to_openai_tools(declarations)
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT_PATH.read_text(encoding="utf-8")},
        *trim_history(history, HISTORY_WINDOW),
        {"role": "user", "content": user_text},
    ]

    turn_record: dict[str, Any] = {
        "turn_index": len(st.session_state["transcript"]["turns"]) + 1,
        "started_at": now_iso(),
        "user": user_text,
        "status": "started",
        "assistant_text": None,
        "rounds": [],
        "tool_events": [],
    }
    try:
        result = run_model_tool_loop(
            provider=provider,
            messages=messages,
            tools=tool_schemas,
            model=settings["model"],
            max_tool_rounds=MAX_TOOL_ROUNDS,
        )
        turn_record.update(result)
        assistant_text = result["assistant_text"] or "The agent did not return a response."
        st.session_state["history"].extend([
            {"role": "user", "content": user_text},
            {"role": "assistant", "content": assistant_text},
        ])
        st.session_state["messages"].extend([
            {"role": "user", "content": user_text},
            {
                "role": "assistant",
                "content": assistant_text,
                "tool_events": result.get("tool_events", []),
            },
        ])
    except Exception as exc:
        error_text = f"{type(exc).__name__}: {exc}"
        turn_record.update({"status": "provider_error", "error": error_text})
        st.session_state["messages"].extend([
            {"role": "user", "content": user_text},
            {"role": "assistant", "content": f"Provider error: `{error_text}`"},
        ])

    turn_record["ended_at"] = now_iso()
    st.session_state["transcript"]["turns"].append(turn_record)
    write_transcript(Path(st.session_state["transcript_path"]), st.session_state["transcript"])


st.markdown(
    '<div class="agent-topline"><div class="agent-mark">R</div><div class="agent-name">Research Agent</div></div>',
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("Settings")
    provider_choice = st.selectbox("Provider", PROVIDERS, index=0)
    model_choice = st.text_input("Model", placeholder="Provider default").strip() or None
    if st.button("New chat", use_container_width=True, type="primary"):
        start_conversation(provider_choice, model_choice)
        st.rerun()

if "transcript" not in st.session_state:
    start_conversation(provider_choice, model_choice)
elif (
    st.session_state["settings"]["provider"] != provider_choice
    or st.session_state["settings"]["model"] != model_choice
):
    st.sidebar.caption("Settings apply to the next chat.")

render_messages()

prompt = st.chat_input("Ask anything to research")
if prompt:
    with st.spinner("Researching..."):
        handle_user_turn(prompt)
    st.rerun()

transcript_path = Path(st.session_state["transcript_path"])

st.sidebar.download_button(
    "Export transcript",
    data=transcript_path.read_text(encoding="utf-8"),
    file_name=transcript_path.name,
    mime="application/json",
    use_container_width=True,
)
