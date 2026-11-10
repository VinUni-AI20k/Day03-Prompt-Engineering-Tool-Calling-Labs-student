import streamlit as st
from chat import ARTIFACTS_DIR, run_model_tool_loop, trim_history
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools

st.set_page_config(page_title="Research Agent - Team BAAE", page_icon="🔎", layout="centered")
st.title("🔎 Research Agent — Assistant & Fact-checker")
st.caption("Day 03 Research Agent: Tra cứu web, mạng xã hội, đọc tài liệu, tính toán và bảo vệ an toàn gửi tin.")

# Tải cấu hình System Prompt và Tools từ artifacts
SYSTEM_PROMPT = (ARTIFACTS_DIR / "system_prompt.md").read_text(encoding="utf-8")
TOOLS = to_openai_tools(load_tool_declarations(ARTIFACTS_DIR / "tools.yaml"))

# Khởi tạo session state
if "provider" not in st.session_state:
    # Mặc định sử dụng provider openai (hoặc openrouter / gemini tùy cấu hình .env)
    st.session_state.provider = make_provider("openai")
    st.session_state.history = []

# Hiển thị lịch sử chat
for msg in st.session_state.history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "tools" in msg and msg["tools"]:
            for call in msg["tools"]:
                with st.expander(f"🔧 Tool called: `{call['name']}`"):
                    st.json(call.get("args", {}))

# Input từ người dùng
if user_text := st.chat_input("Hỏi agent về tin tức, bài viết, tính toán..."):
    st.chat_message("user").markdown(user_text)
    
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        *trim_history(st.session_state.history, 5),
        {"role": "user", "content": user_text}
    ]
    
    with st.spinner("Agent đang suy nghĩ và thực thi công cụ..."):
        result = run_model_tool_loop(
            provider=st.session_state.provider,
            messages=messages,
            tools=TOOLS,
            model=None,
            max_tool_rounds=4
        )
    
    # Gom danh sách các tool đã được gọi trong lượt này
    called_tools = []
    for r in result.get("rounds", []):
        for call in r.get("tool_calls", []):
            called_tools.append(call)
            
    with st.chat_message("assistant"):
        # Hiện chi tiết tool call dạng expander (yêu cầu Rubric: không che lỗi/che tool)
        for call in called_tools:
            with st.expander(f"🔧 Đã thực thi tool: `{call['name']}`", expanded=True):
                st.write("**Tham số truyền vào (Arguments):**")
                st.json(call.get("args", {}))
        
        st.markdown(result["assistant_text"])
    
    # Lưu vào lịch sử hội thoại
    st.session_state.history.append({"role": "user", "content": user_text})
    st.session_state.history.append({
        "role": "assistant",
        "content": result["assistant_text"],
        "tools": called_tools
    })