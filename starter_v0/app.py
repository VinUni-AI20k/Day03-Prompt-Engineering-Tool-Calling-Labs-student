import streamlit as st

from chat_service import ChatSession


# ---------------------------------------
# 1. Page configuration
# ---------------------------------------

st.set_page_config(
    page_title="Research Agent",
    page_icon="🔎",
    layout="centered",
)

st.title("🔎 Research Agent")
st.caption("AI-powered research assistant")


# ---------------------------------------
# 2. Sidebar
# ---------------------------------------

with st.sidebar:
    st.header("Settings")

    st.write("**Provider:** OpenRouter")
    st.write("**Agent version:** v0")

    if st.button("New conversation", use_container_width=True):
        st.session_state.chat_session = ChatSession(
            provider_name="openrouter",
            version="v0",
        )
        st.session_state.messages = []
        st.rerun()


# ---------------------------------------
# 3. Initialize chat session
# ---------------------------------------

if "chat_session" not in st.session_state:
    st.session_state.chat_session = ChatSession(
        provider_name="openrouter",
        version="v0",
    )

if "messages" not in st.session_state:
    st.session_state.messages = []


chat_session = st.session_state.chat_session


# ---------------------------------------
# 4. Display previous messages
# ---------------------------------------

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# ---------------------------------------
# 5. Chat input
# ---------------------------------------

if prompt := st.chat_input("Nhập câu hỏi của bạn..."):

    # Display user message
    st.session_state.messages.append({
        "role": "user",
        "content": prompt,
    })

    with st.chat_message("user"):
        st.markdown(prompt)

    # Call Research Agent
    with st.chat_message("assistant"):

        with st.spinner("Research Agent đang xử lý..."):
            result = chat_session.send_message(prompt)

        status = result.get("status")
        answer = result.get("assistant_text") or ""

        if status == "provider_error":
            st.error(
                result.get("error", "Không thể gọi provider.")
            )

        else:
            st.markdown(answer)

            st.session_state.messages.append({
                "role": "assistant",
                "content": answer,
            })

        # Show tool execution details
        tool_events = result.get("tool_events", [])

        if tool_events:
            with st.expander("🔧 Tool execution details"):
                st.json(tool_events)

        # Show status
        st.caption(f"Status: {status}")


# ---------------------------------------
# 6. Transcript information
# ---------------------------------------

with st.sidebar:
    st.divider()
    st.caption("Transcript")
    st.code(chat_session.transcript_id)

    st.caption("Saved at:")
    st.code(str(chat_session.transcript_path))
