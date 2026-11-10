from __future__ import annotations

import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any

import streamlit as st

from env_loader import load_lab_env
from providers import make_provider
from providers.base import ToolCall
from tools import TOOL_FUNCTIONS, load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version

# Root paths
ROOT = Path(__file__).parent
ARTIFACTS_DIR = ROOT / "artifacts"
TRANSCRIPTS_DIR = ROOT / "transcripts"
TRANSCRIPTS_DIR.mkdir(parents=True, exist_ok=True)

# Load environment
load_lab_env(ROOT)

# Page configuration
st.set_page_config(
    page_title="Research Agent UI",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for polished, modern UX
st.markdown(
    """
    <style>
    /* Main container styling */
    .block-container {
        padding-top: 1.8rem;
        padding-bottom: 2.5rem;
        max-width: 1200px;
    }
    
    /* Header card */
    .agent-header {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        color: #ffffff;
        padding: 1.25rem 1.5rem;
        border-radius: 12px;
        margin-bottom: 1.25rem;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    .agent-header h2 {
        color: #38bdf8;
        margin: 0;
        font-size: 1.6rem;
        font-weight: 700;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    .agent-header p {
        margin: 0.35rem 0 0 0;
        color: #94a3b8;
        font-size: 0.95rem;
    }

    /* Badges */
    .badge-pill {
        display: inline-block;
        padding: 0.2rem 0.6rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-right: 0.4rem;
    }
    .badge-provider {
        background-color: #0284c7;
        color: white;
    }
    .badge-version {
        background-color: #10b981;
        color: white;
    }
    .badge-tool {
        background-color: #6366f1;
        color: white;
    }

    /* Clarification box */
    .clarify-banner {
        background-color: #fffbeb;
        border-left: 4px solid #f59e0b;
        color: #92400e;
        padding: 1rem 1.25rem;
        border-radius: 8px;
        margin: 0.8rem 0;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    
    /* Tool result cards */
    .tool-box {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 0.75rem;
        margin: 0.5rem 0;
        font-size: 0.88rem;
    }

    /* Quick question pill buttons */
    div[data-testid="stHorizontalBlock"] button {
        border-radius: 20px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def safe_slug(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9_.-]+", "_", value.strip())
    return slug.strip("_") or "run"


def execute_tool_call(call: ToolCall) -> dict[str, Any]:
    func = TOOL_FUNCTIONS.get(call.name)
    if not func:
        return {
            "tool": call.name,
            "args": call.args,
            "result": {
                "error": "unknown_tool",
                "message": f"No local implementation for {call.name}",
            },
        }
    try:
        result = func(**call.args)
    except Exception as exc:
        result = {"error": type(exc).__name__, "message": str(exc)}
    return {"tool": call.name, "args": call.args, "result": result}


def tool_results_message(events: list[dict[str, Any]]) -> dict[str, str]:
    text = json.dumps(events, ensure_ascii=False, indent=2, default=str)
    if len(text) > 24000:
        text = text[:24000] + "\n...<truncated>"
    return {
        "role": "user",
        "content": (
            "TOOL_RESULTS_JSON:\n"
            f"{text}\n\n"
            "Use only these tool results. If the user asked for a digest and the items are ready, "
            "call the formatting tool. Otherwise answer the user directly with cited sources when available."
        ),
    }


def assistant_tool_message(response_text: str | None, calls: list[ToolCall]) -> dict[str, str]:
    call_summary = [{"name": call.name, "args": call.args} for call in calls]
    content = response_text or "I will call the selected tool(s)."
    return {
        "role": "assistant",
        "content": f"{content}\n\nTOOL_CALLS_JSON:\n{json.dumps(call_summary, ensure_ascii=False, indent=2)}",
    }


def write_transcript(path: Path, transcript: dict[str, Any]) -> None:
    transcript["updated_at"] = now_iso()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(transcript, ensure_ascii=False, indent=2, default=str), encoding="utf-8")


# ---------------- Sidebar Configuration ----------------
with st.sidebar:
    st.title("⚙️ Cấu hình Agent")

    provider_name = st.selectbox(
        "Provider",
        options=["gemini", "openrouter", "openai", "anthropic", "ollama"],
        index=0 if os.getenv("GEMINI_API_KEY") else 1,
        help="Chọn AI Provider xử lý câu lệnh và tool calls.",
    )

    default_models = {
        "gemini": "gemini-2.5-flash",
        "openrouter": "openrouter/auto",
        "openai": "gpt-4o-mini",
        "anthropic": "claude-3-5-haiku-20241022",
        "ollama": "qwen2.5:7b",
    }
    model_name = st.text_input(
        "Model Name",
        value=default_models.get(provider_name, ""),
        help="Để trống sẽ dùng model mặc định của Provider.",
    )

    version_label = st.selectbox(
        "Phiên bản Artifact (Version)",
        options=["v0", "v1", "v2", "v3"],
        index=0,
        help="Ghi nhận version đánh giá trong version_log.csv.",
    )

    system_prompt_path = ARTIFACTS_DIR / "system_prompt.md"
    tools_yaml_path = ARTIFACTS_DIR / "tools.yaml"

    col_s1, col_s2 = st.columns(2)
    with col_s1:
        history_window = st.number_input("History pairs", min_value=1, max_value=20, value=5)
    with col_s2:
        max_tool_rounds = st.number_input("Max rounds", min_value=1, max_value=8, value=4)

    st.markdown("---")
    st.subheader("🔑 Trạng thái API Keys")
    keys_status = [
        ("Gemini", bool(os.getenv("GEMINI_API_KEY"))),
        ("OpenRouter", bool(os.getenv("OPENROUTER_API_KEY"))),
        ("Tavily (Web Search)", bool(os.getenv("Tavily_API_KEY") or os.getenv("TAVILY_API_KEY"))),
        ("Firecrawl (Reader)", bool(os.getenv("FIRECRAWL_API_KEY"))),
        ("RapidAPI (Twitter)", bool(os.getenv("RAPIDAPI_KEY"))),
        ("Telegram Bot", bool(os.getenv("TELEGRAM_BOT_TOKEN"))),
    ]
    for name, is_set in keys_status:
        icon = "🟢" if is_set else "⚪"
        st.write(f"{icon} **{name}**: {'Sẵn sàng' if is_set else 'Chưa cấu hình'}")

    st.markdown("---")
    st.subheader("🛠️ Danh sách Tool đang nạp")
    try:
        declarations = load_tool_declarations(tools_yaml_path)
        for t in declarations:
            with st.expander(f"🔧 {t['name']}"):
                st.caption(t.get("description", "Không có mô tả."))
                st.code(json.dumps(t.get("parameters", {}), ensure_ascii=False, indent=2), language="json")
    except Exception as e:
        st.error(f"Lỗi đọc tools.yaml: {e}")

    st.markdown("---")
    if st.button("🗑️ Xóa lịch sử chat & làm mới", use_container_width=True):
        st.session_state.messages = []
        st.session_state.chat_history = []
        st.session_state.awaiting_user_action = None
        st.session_state.transcript = None
        st.rerun()


# ---------------- Session State Initialization ----------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "awaiting_user_action" not in st.session_state:
    st.session_state.awaiting_user_action = None

if "transcript" not in st.session_state or st.session_state.transcript is None:
    try:
        artifact_ver = build_artifact_version(version_label, system_prompt_path, tools_yaml_path)
    except Exception:
        artifact_ver = None

    ts = datetime.now().strftime("%Y%m%dT%H%M%S%f")
    transcript_id = f"{safe_slug(version_label)}_{safe_slug(provider_name)}_{ts}"
    transcript_path = TRANSCRIPTS_DIR / f"{transcript_id}.transcript.json"

    st.session_state.transcript_path = str(transcript_path)
    st.session_state.transcript = {
        "transcript_id": transcript_id,
        **(artifact_version_dict(artifact_ver) if artifact_ver else {}),
        "provider": provider_name,
        "model": model_name or None,
        "system_prompt": str(system_prompt_path),
        "tools": str(tools_yaml_path),
        "history_window": history_window,
        "max_tool_rounds": max_tool_rounds,
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "turns": [],
    }

# ---------------- Header Presentation ----------------
st.markdown(
    f"""
    <div class="agent-header">
        <h2>🔬 Research Agent Interactive Workspace</h2>
        <p>Hệ thống nghiên cứu thông minh đa công cụ (Multi-Tool Autonomous Agent) với bằng chứng thực nghiệm & JSON Log.</p>
        <div style="margin-top: 0.75rem;">
            <span class="badge-pill badge-provider">Provider: {provider_name.upper()}</span>
            <span class="badge-pill badge-version">Version: {version_label}</span>
            <span class="badge-pill badge-tool">Tools Loaded: {len(TOOL_FUNCTIONS)}</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------- Quick Prompt Suggestions ----------------
st.markdown("**Gợi ý thử nhanh:**")
col_p1, col_p2, col_p3, col_p4 = st.columns(4)

selected_prompt = None
with col_p1:
    if st.button("📰 Tin AI mới nhất", use_container_width=True):
        selected_prompt = "Tìm kiếm các tin tức AI quan trọng nhất trong tuần qua và tóm tắt theo gạch đầu dòng."
with col_p2:
    if st.button("🐦 Tweet @sama", use_container_width=True):
        selected_prompt = "Lấy các bài đăng gần đây của Sam Altman (@sama) trên X."
with col_p3:
    if st.button("🔍 Thảo luận DeepSeek", use_container_width=True):
        selected_prompt = "Tìm các thảo luận nổi bật nhất về DeepSeek trên mạng xã hội X."
with col_p4:
    if st.button("📚 Nghiên cứu ArXiv", use_container_width=True):
        selected_prompt = "Tìm 3 bài nghiên cứu mới nhất về LLM Tool Calling trên ArXiv."


# ---------------- Render Existing Conversation ----------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="🧑‍💻" if msg["role"] == "user" else "🤖"):
        # If there are tool calls in this turn, render them nicely
        if msg.get("tool_events"):
            for event in msg["tool_events"]:
                tool_name = event.get("tool", "tool")
                args = event.get("args", {})
                res = event.get("result", {})
                
                # Check icons
                icons = {
                    "lookup": "🔍",
                    "social_search": "🐦",
                    "timeline": "⏱️",
                    "fetch": "📄",
                    "papers": "📚",
                    "paper_text": "📖",
                    "policy": "🏢",
                    "clarify": "💬",
                    "send": "✈️",
                    "format": "📊",
                }
                tool_icon = icons.get(tool_name, "🔧")
                with st.expander(f"{tool_icon} Tool Executed: `{tool_name}`", expanded=False):
                    st.markdown("**Tham số (Arguments):**")
                    st.json(args)
                    st.markdown("**Kết quả thực tế (Tool Result):**")
                    st.json(res)

        st.markdown(msg["content"])


# ---------------- Clarification / Confirmation UI Banner ----------------
if st.session_state.awaiting_user_action:
    act = st.session_state.awaiting_user_action
    st.markdown(
        f"""
        <div class="clarify-banner">
            <strong>⚠️ Yêu cầu từ Agent ({act.get('type', 'Clarification')}):</strong><br>
            {act.get('question', 'Vui lòng cung cấp thêm thông tin để tiếp tục.')}
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    # If options or yes/no
    options = act.get("options", [])
    resp_type = act.get("response_type", "text")
    if resp_type == "yes_no" or not options and "xác nhận" in act.get("question", "").lower():
        options = ["Đồng ý / Xác nhận", "Hủy bỏ"]

    if options:
        opt_cols = st.columns(len(options))
        for idx, opt in enumerate(options):
            with opt_cols[idx]:
                if st.button(f"👉 {opt}", key=f"clarify_opt_{idx}", use_container_width=True):
                    selected_prompt = opt
                    st.session_state.awaiting_user_action = None


# ---------------- Execution Engine ----------------
def run_agent_turn(user_input: str):
    # Append user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    st.session_state.awaiting_user_action = None

    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(user_input)

    # Prepare agent run
    with st.chat_message("assistant", avatar="🤖"):
        status_box = st.status("🧠 Agent đang phân tích và chọn tool...", expanded=True)
        
        try:
            # Load fresh declarations and prompt
            system_prompt = system_prompt_path.read_text(encoding="utf-8")
            tool_declarations = load_tool_declarations(tools_yaml_path)
            openai_tools = to_openai_tools(tool_declarations)
            provider = make_provider(provider_name)
            selected_model = model_name or getattr(provider, "default_model", None)

            # Build messages window
            trimmed_history = st.session_state.chat_history[-history_window * 2 :]
            working_messages = [
                {"role": "system", "content": system_prompt},
                *trimmed_history,
            ]

            turn_record: dict[str, Any] = {
                "turn_index": len(st.session_state.transcript.get("turns", [])) + 1,
                "started_at": now_iso(),
                "user": user_input,
                "status": "started",
                "assistant_text": None,
                "rounds": [],
                "tool_events": [],
            }

            rounds: list[dict[str, Any]] = []
            all_tool_events: list[dict[str, Any]] = []
            final_text = ""
            status_result = "answered"

            for round_idx in range(1, max_tool_rounds + 1):
                status_box.update(label=f"🔄 Vòng gọi Tool #{round_idx}/{max_tool_rounds}...")
                
                resp = provider.complete(
                    working_messages,
                    openai_tools,
                    model=selected_model,
                    temperature=0.0,
                )
                calls = resp.tool_calls
                round_record: dict[str, Any] = {
                    "round": round_idx,
                    "assistant_text": resp.text,
                    "tool_calls": [{"name": c.name, "args": c.args} for c in calls],
                    "tool_results": [],
                }

                if not calls:
                    rounds.append(round_record)
                    final_text = resp.text or ""
                    status_result = "answered"
                    break

                working_messages.append(assistant_tool_message(resp.text, calls))
                non_clarification_events: list[dict[str, Any]] = []
                clarify_triggered = False

                for call in calls:
                    status_box.write(f"⚙️ Đang thực thi tool: **{call.name}**...")
                    event = execute_tool_call(call)
                    round_record["tool_results"].append(event)
                    all_tool_events.append(event)

                    result = event.get("result", {})
                    if isinstance(result, dict) and result.get("awaiting_user"):
                        q = result.get("question") or call.args.get("question") or "Bạn bổ sung thêm thông tin nhé."
                        final_text = q
                        status_result = "waiting_for_user"
                        st.session_state.awaiting_user_action = {
                            "type": "Clarification",
                            "question": q,
                            "response_type": call.args.get("response_type", "text"),
                            "options": call.args.get("options", []),
                        }
                        clarify_triggered = True
                        break

                    non_clarification_events.append(event)

                rounds.append(round_record)
                if clarify_triggered:
                    break

                working_messages.append(tool_results_message(non_clarification_events))
            else:
                status_result = "max_tool_rounds"
                final_text = f"Đã dừng sau {max_tool_rounds} vòng gọi công cụ."

            status_box.update(label="✅ Hoàn tất lượt xử lý!", state="complete", expanded=False)

            # Display final text
            st.markdown(final_text)

            # Record turn
            turn_record.update({
                "status": status_result,
                "assistant_text": final_text,
                "rounds": rounds,
                "tool_events": all_tool_events,
                "ended_at": now_iso(),
            })

            # Save in transcript
            st.session_state.transcript["turns"].append(turn_record)
            write_transcript(Path(st.session_state.transcript_path), st.session_state.transcript)

            # Add to session messages
            st.session_state.messages.append({
                "role": "assistant",
                "content": final_text,
                "tool_events": all_tool_events,
            })
            st.session_state.chat_history.append({"role": "assistant", "content": final_text})

        except Exception as exc:
            status_box.update(label="❌ Lỗi xảy ra!", state="error", expanded=True)
            err_msg = f"{type(exc).__name__}: {str(exc)}"
            st.error(err_msg)
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"⚠️ Đã có lỗi xảy ra: {err_msg}",
            })


# ---------------- User Input Handling ----------------
prompt = st.chat_input("Hỏi research agent hoặc nhập chỉ dẫn...")
actual_input = selected_prompt or prompt

if actual_input:
    run_agent_turn(actual_input)
    st.rerun()

# ---------------- Bottom Bar: Transcript Download & Status ----------------
st.markdown("---")
b_col1, b_col2 = st.columns([3, 1])
with b_col1:
    turns_count = len(st.session_state.transcript.get("turns", []))
    st.caption(f"📝 Phiên làm việc: `{st.session_state.transcript.get('transcript_id')}` | Số lượt: `{turns_count}`")
with b_col2:
    transcript_json = json.dumps(st.session_state.transcript, ensure_ascii=False, indent=2)
    st.download_button(
        label="💾 Tải Transcript JSON",
        data=transcript_json,
        file_name=f"{st.session_state.transcript.get('transcript_id')}.transcript.json",
        mime="application/json",
        use_container_width=True,
    )

