
import streamlit as st

from utils.api import ask_agent
from utils.common import (
    initialize_session,
    show_dataset_selector
)


st.set_page_config(
    page_title="AI Financial Assistant",
    page_icon="🤖",
    layout="wide"
)

initialize_session()

st.title("🤖 AI Financial Assistant")
st.caption(
    "Ask questions about your financial data and receive "
    "AI-powered insights using Groq, RAG and specialized agents."
)

dataset_id = show_dataset_selector()

if not dataset_id:
    st.warning("Please upload or select a dataset first.")
    st.stop()

# Reset conversation when the selected dataset changes
if st.session_state.get("chat_dataset_id") != dataset_id:
    st.session_state.chat_dataset_id = dataset_id
    st.session_state.messages = []

# Suggested questions
st.subheader("Suggested Questions")

suggestions = [
    "Which product generated the highest revenue?",
    "Which country generated the highest profit?",
    "Why is the Enterprise segment making losses?",
    "Give me an overall financial performance summary.",
    "What are the expected profits for the next three months?"
]

cols = st.columns(2)

for index, question in enumerate(suggestions):
    with cols[index % 2]:
        if st.button(question, key=f"suggestion_{index}"):
            st.session_state.pending_question = question

st.divider()

# Display conversation history
st.subheader("Chat with your Financial Assistant")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

        if message["role"] == "assistant":
            if message.get("agent"):
                st.caption(
                    f'Agent: {message["agent"]} | '
                    f'Analysis: {message.get("analysis_type", "N/A")}'
                )

            sources = message.get("sources", [])

            if sources:
                with st.expander("Retrieved Knowledge Sources"):
                    for source in sources:
                        st.markdown(
                            f'**{source.get("name", "Unknown")}** '
                            f'({source.get("category", "N/A")})'
                        )

# Question input
prompt = st.chat_input("Ask a question about your financial data...")

if st.session_state.get("pending_question"):
    prompt = st.session_state.pending_question
    del st.session_state.pending_question

if prompt:
    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Analyzing your financial data..."):
            response = ask_agent(dataset_id, prompt)

        if response and response.get("status") == "success":
            result = response.get("result", {})
            answer = result.get("answer", "No answer was returned.")

            st.markdown(answer)

            agent = response.get("agent", "Unknown")
            analysis_type = response.get("analysis_type", "N/A")
            sources = result.get("sources", [])

            st.caption(
                f"Agent: {agent} | Analysis: {analysis_type}"
            )

            if sources:
                with st.expander("Retrieved Knowledge Sources"):
                    for source in sources:
                        st.markdown(
                            f'**{source.get("name", "Unknown")}** '
                            f'({source.get("category", "N/A")})'
                        )

            st.session_state.messages.append({
                "role": "assistant",
                "content": answer,
                "agent": agent,
                "analysis_type": analysis_type,
                "sources": sources
            })

        else:
            error_message = (
                response.get("error", "The AI request failed.")
                if response else
                "Unable to connect to the AI backend."
            )

            st.error(error_message)

            st.session_state.messages.append({
                "role": "assistant",
                "content": f"Error: {error_message}"
            })

# Clear conversation
if st.session_state.messages:
    if st.button("Clear Conversation"):
        st.session_state.messages = []
        st.rerun()
