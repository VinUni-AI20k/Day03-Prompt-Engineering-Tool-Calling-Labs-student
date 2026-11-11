from __future__ import annotations

import os
import json
from datetime import datetime
from pathlib import Path
from typing import Any

import streamlit as st

# Local modules
from env_loader import load_lab_env
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from chat import (
    execute_tool_call,
    run_model_tool_loop,
    write_transcript,
    now_iso,
    safe_slug,
    ROOT,
    ARTIFACTS_DIR,
)

# Ensure environment variables are loaded
load_lab_env(ROOT)

# ---------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------
st.set_page_config(
    page_title="Research Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Clean Styling (Warm Minimalist Theme, Zero Star Icons)
THEME_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;1,6..72,400&family=Inter:wght@400;500;600&display=swap');

:root {
    --bg-color: #FBF9F5;
    --surface-color: #FFFFFF;
    --sidebar-color: #F3EFE6;
    --text-color: #2B2823;
    --text-muted: #726E67;
    --accent-color: #2B2823;
    --accent-hover: #4A463F;
    --border-color: #E8E3D8;
    --card-color: #FAF6EF;
}

/* Background & Body */
.stApp {
    background-color: var(--bg-color);
    color: var(--text-color);
    font-family: 'Inter', -apple-system, sans-serif;
}

/* Header */
.custom-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1.2rem 0 1.5rem 0;
    border-bottom: 1px solid var(--border-color);
    margin-bottom: 1.5rem;
}
.brand-group {
    display: flex;
    align-items: center;
    gap: 12px;
}
.brand-title {
    font-family: 'Newsreader', Georgia, serif;
    font-size: 26px;
    font-weight: 500;
    color: var(--text-color);
    letter-spacing: -0.02em;
    margin: 0;
}
.badge {
    background-color: var(--sidebar-color);
    color: var(--text-muted);
    font-size: 12.5px;
    font-weight: 500;
    padding: 4px 12px;
    border-radius: 999px;
    border: 1px solid var(--border-color);
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: var(--sidebar-color);
    border-right: 1px solid var(--border-color);
}
section[data-testid="stSidebar"] hr {
    border-color: var(--border-color);
}

/* Message styling */
.stChatMessage {
    background-color: transparent !important;
    border: none !important;
    padding: 0.8rem 0 !important;
}

div[data-testid="stChatMessage"][data-test-user="true"] {
    background-color: #F0ECE1 !important;
    border-radius: 18px !important;
    padding: 12px 18px !important;
    max-width: 85%;
    margin-left: auto;
}

.assistant-response {
    font-size: 15.5px;
    line-height: 1.68;
    color: var(--text-color);
}

/* Input Box */
div[data-testid="stChatInput"] {
    border-color: var(--border-color);
    border-radius: 24px;
    box-shadow: 0 4px 14px rgba(0,0,0,0.03);
}

button[kind="primary"] {
    background-color: var(--accent-color) !important;
    border-color: var(--accent-color) !important;
    color: #FFFFFF !important;
    border-radius: 8px !important;
    font-weight: 500 !important;
}
button[kind="primary"]:hover {
    background-color: var(--accent-hover) !important;
}
</style>
"""
st.markdown(THEME_CSS, unsafe_allow_html=True)


# ---------------------------------------------------------
# Session State Initialization
# ---------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "transcript_id" not in st.session_state:
    st.session_state.transcript_id = datetime.now().strftime("%Y%m%d_%H%M%S")

if "transcript_data" not in st.session_state:
    st.session_state.transcript_data = {
        "transcript_id": st.session_state.transcript_id,
        "started_at": now_iso(),
        "turns": [],
    }

# Initialize provider to get default model
gemini_provider = make_provider("gemini")
configured_model = os.getenv("GEMINI_MODEL") or getattr(gemini_provider, "default_model", "gemini-3.5-flash-lite")

# Helper to load available versions from version_log.csv
def get_available_versions() -> list[dict[str, str]]:
    version_log_path = ARTIFACTS_DIR / "version_log.csv"
    versions = []
    if version_log_path.exists():
        try:
            with open(version_log_path, encoding="utf-8") as f:
                reader = list(csv.DictReader(f))
                for row in reader:
                    v = row.get("version", "").strip()
                    if v and v not in [item["version"] for item in versions]:
                        versions.append({
                            "version": v,
                            "metric": row.get("metric_after", ""),
                            "hypothesis": row.get("hypothesis", ""),
                        })
        except Exception:
            pass
    return versions


def get_system_prompt_for_version(version: str) -> tuple[str, str]:
    """Tự động tải system prompt tương ứng với version được chọn."""
    version_specific_path = ARTIFACTS_DIR / f"system_prompt_{version}.md"
    if version_specific_path.exists():
        return version_specific_path.read_text(encoding="utf-8"), version_specific_path.name

    default_path = ARTIFACTS_DIR / "system_prompt.md"
    if default_path.exists():
        return default_path.read_text(encoding="utf-8"), default_path.name
    return "", "none"


def get_tools_for_version(version: str) -> list[dict[str, Any]]:
    """Tải cấu hình tools tương ứng với version được chọn (nếu có riêng)."""
    v_tools_path = ARTIFACTS_DIR / f"tools_{version}.yaml"
    if v_tools_path.exists():
        return load_tool_declarations(v_tools_path)
    default_tools_path = ARTIFACTS_DIR / "tools.yaml"
    if default_tools_path.exists():
        return load_tool_declarations(default_tools_path)
    return []


# ---------------------------------------------------------
# Sidebar Controls (Only Your Model)
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("### **Agent Settings**")
    st.caption("Research Agent · Tool Calling Loop")

    # Editable Model ID to match user's exact model
    model_name = st.text_input(
        "Model ID",
        value=configured_model,
        help="Nhập chính xác tên model của bạn (ví dụ: gemini-3.5-flash-lite, gemini-2.5-flash, gemini-1.5-flash...)",
    )

    available_versions = get_available_versions()
    version_keys = [item["version"] for item in available_versions]
    for standard_v in ["v0", "v1", "v2", "v3"]:
        if standard_v not in version_keys:
            version_keys.append(standard_v)

    # Set default to highest available in log or v2
    default_idx = len(version_keys) - 1
    if "v2" in version_keys:
        default_idx = version_keys.index("v2")

    version_tag = st.selectbox(
        "Evaluation Version Tag",
        options=version_keys,
        index=default_idx,
        help="Chọn version (v0, v1, v2, v3) để thực thi và ghi vào transcript.",
    )

    # Toast feedback when version changes
    if "active_version" not in st.session_state:
        st.session_state.active_version = version_tag
    elif st.session_state.active_version != version_tag:
        st.session_state.active_version = version_tag
        st.toast(f"Đã chuyển sang {version_tag} — System Prompt đã cập nhật tức thì!", icon="⚙️")

    matching_info = next((item for item in available_versions if item["version"] == version_tag), None)
    if matching_info and matching_info.get("metric"):
        st.markdown(
            f"""
            <div style="background-color: #FFFFFF; border: 1px solid #E8E3D8; border-radius: 8px; padding: 8px 12px; margin-top: 6px; font-size: 12px;">
                <span style="color: #726E67;">Đo lường {version_tag}:</span><br/>
                <b>Kết quả:</b> <code>{matching_info['metric']}</code>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("---")
    st.markdown("#### ⚙️ **Active Artifacts**")

    # Load version-specific system prompt & tool declarations
    sys_prompt_text, prompt_filename = get_system_prompt_for_version(version_tag)
    with st.expander(f"📄 System Prompt ({version_tag})"):
        st.caption(f"📁 Tệp nguồn: `{prompt_filename}`")
        st.code(sys_prompt_text, language="markdown")

    tool_decls = get_tools_for_version(version_tag)
    with st.expander(f"🛠️ Declared Tools ({len(tool_decls)})"):
        for t in tool_decls:
            st.markdown(f"**`{t['name']}`**: {t.get('description', '')}")

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ Reset Chat", use_container_width=True):
            st.session_state.messages = []
            st.session_state.transcript_id = datetime.now().strftime("%Y%m%d_%H%M%S")
            st.session_state.transcript_data = {
                "transcript_id": st.session_state.transcript_id,
                "started_at": now_iso(),
                "turns": [],
            }
            st.rerun()

    with col2:
        st.caption("💾 Transcript Auto-saved")


# ---------------------------------------------------------
# Top Header (Clean Minimalist, No Orange Star)
# ---------------------------------------------------------
st.markdown(
    f"""
    <div class="custom-header">
        <div class="brand-group">
            <span class="brand-title">Research Assistant</span>
            <span class="badge">{model_name} · {version_tag}</span>
        </div>
        <div class="badge">
            {len(tool_decls)} Tools Available
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# Starter Suggestions if Empty (No Orange Star Icon)
# ---------------------------------------------------------
if not st.session_state.messages:
    st.markdown(
        """
        <div style="text-align: center; margin: 3rem 0 2rem 0;">
            <h2 style="font-family: 'Newsreader', Georgia, serif; font-size: 28px; font-weight: 500; color: #2B2823; margin-bottom: 8px;">
                Tôi có thể giúp gì cho nghiên cứu của bạn hôm nay?
            </h2>
            <p style="color: #726E67; font-size: 14.5px; max-width: 520px; margin: 0 auto 1.5rem auto;">
                Tìm kiếm bài đăng mạng xã hội, tổng hợp tin tức web thời gian thực, đọc URL và trích xuất dữ liệu khoa học.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)
    sample_queries = [
        ("📰 Tin tức AI hôm nay", "Tin tức AI hôm nay có gì nổi bật?"),
        ("🐦 Tweet mới nhất", "Tweet mới nhất của Sam Altman là gì?"),
        ("📊 Thảo luận GPT-5", "Mọi người đang bàn gì về GPT-5 trên Twitter?"),
    ]

    for col, (label, query) in zip([col1, col2, col3], sample_queries):
        with col:
            if st.button(label, use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": query})
                st.session_state.pending_query = query
                st.rerun()


# ---------------------------------------------------------
# Render Message History
# ---------------------------------------------------------
for msg in st.session_state.messages:
    role = msg["role"]
    avatar = "👤" if role == "user" else "🤖"

    with st.chat_message(role, avatar=avatar):
        tool_events = msg.get("tool_events", [])

        if tool_events:
            with st.expander(f"🔧 **Tool Execution ({len(tool_events)} calls)**", expanded=False):
                for event in tool_events:
                    tool_name = event.get("tool", "unknown")
                    args = event.get("args", {})
                    result = event.get("result", {})
                    st.markdown(f"**Tool:** `{tool_name}`")
                    st.json({"arguments": args, "result": result}, expanded=False)

        st.markdown(f"<div class='assistant-response'>{msg['content']}</div>", unsafe_allow_html=True)


# ---------------------------------------------------------
# User Input & Execution Pipeline
# ---------------------------------------------------------
prompt = st.chat_input("Nhập câu hỏi hoặc yêu cầu nghiên cứu của bạn...")

if hasattr(st.session_state, "pending_query") and st.session_state.pending_query:
    prompt = st.session_state.pending_query
    del st.session_state.pending_query

if prompt:
    if not (st.session_state.messages and st.session_state.messages[-1]["role"] == "user" and st.session_state.messages[-1]["content"] == prompt):
        st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="🤖"):
        status_placeholder = st.empty()
        status_placeholder.markdown("*(Đang phân tích & định tuyến tools...)*")

        try:
            # Uses user's Gemini provider and chosen model
            provider = gemini_provider
            tools_json = to_openai_tools(tool_decls)

            # Build history for multi-turn
            history = []
            for m in st.session_state.messages[:-1]:
                history.append({"role": m["role"], "content": m["content"]})
            history.append({"role": "user", "content": prompt})

            messages_payload = [{"role": "system", "content": sys_prompt_text}, *history]

            # Execute tool calling loop with the user's exact model
            outcome = run_model_tool_loop(
                provider=provider,
                messages=messages_payload,
                tools=tools_json,
                model=model_name.strip() if model_name else None,
                max_tool_rounds=3,
            )

            status_placeholder.empty()

            assistant_text = outcome.get("assistant_text", "")
            tool_events = outcome.get("tool_events", [])
            rounds = outcome.get("rounds", [])

            if tool_events:
                with st.expander(f"🔧 **Tool Execution ({len(tool_events)} calls)**", expanded=False):
                    for event in tool_events:
                        tool_name = event.get("tool", "unknown")
                        args = event.get("args", {})
                        result = event.get("result", {})
                        st.markdown(f"**Tool:** `{tool_name}`")
                        st.json({"arguments": args, "result": result}, expanded=False)

            st.markdown(f"<div class='assistant-response'>{assistant_text}</div>", unsafe_allow_html=True)

            # Save to messages history
            st.session_state.messages.append({
                "role": "assistant",
                "content": assistant_text,
                "tool_events": tool_events,
                "rounds": rounds,
            })

            # Save transcript to file (Requirement for Lab submission)
            turn_number = len(st.session_state.transcript_data["turns"]) + 1
            st.session_state.transcript_data["turns"].append({
                "turn": turn_number,
                "user": prompt,
                "assistant": assistant_text,
                "status": outcome.get("status"),
                "rounds": rounds,
            })

            transcript_filename = f"{st.session_state.transcript_id}_{safe_slug(prompt[:25])}.transcript.json"
            transcript_path = ROOT / "transcripts" / transcript_filename
            write_transcript(transcript_path, st.session_state.transcript_data)

        except Exception as e:
            status_placeholder.empty()
            st.error(f"⚠️ Lỗi thực thi agent: {str(e)}")
