import streamlit as st

from utils.api import fetch_datasets

def initialize_session():

    if "dataset_id" not in st.session_state:
        st.session_state.dataset_id = None

    if "datasets" not in st.session_state:
        st.session_state.datasets = []


def load_datasets():

    datasets = fetch_datasets()

    if datasets is None:
        st.error("Unable to load datasets. Check the backend.")
        return []

    st.session_state.datasets = datasets

    if datasets:

        available_ids = [
            dataset["dataset_id"]
            for dataset in datasets
        ]

        if st.session_state.dataset_id not in available_ids:
            st.session_state.dataset_id = available_ids[0]

    return datasets


def get_selected_dataset():

    return st.session_state.get("dataset_id")


def show_dataset_selector():

    datasets = load_datasets()

    if not datasets:
        st.warning("Upload a dataset to continue.")
        return None

    dataset_options = {
        dataset["filename"] + " (" + dataset["dataset_id"][:8] + ")":
        dataset["dataset_id"]
        for dataset in datasets
    }

    current_id = st.session_state.dataset_id

    current_index = list(dataset_options.values()).index(current_id)

    selected_label = st.selectbox(
        "Select Financial Dataset",
        options=list(dataset_options.keys()),
        index=current_index
    )

    st.session_state.dataset_id = dataset_options[selected_label]

    return st.session_state.dataset_id


def render_floating_assistant():

    import streamlit as st
    from utils.api import ask_agent

    # Floating button positioning
    st.markdown(
        """
        <style>
        .st-key-floating_ai {
            position: fixed;
            bottom: 25px;
            right: 25px;
            z-index: 999999;
            width: auto;
        }

        .st-key-floating_ai [data-testid="stPopover"] > button {
            border-radius: 30px;
            padding: 12px 20px;
            box-shadow: 0 4px 14px rgba(0,0,0,0.25);
            font-weight: 600;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    if "floating_messages" not in st.session_state:
        st.session_state.floating_messages = []

    with st.container(key="floating_ai"):

        with st.popover("🤖 Ask AI Assistant"):

            st.subheader("Financial AI Assistant")

            dataset_id = st.session_state.get("dataset_id")

            if not dataset_id:
                st.warning("Please select or upload a dataset first.")

            else:

                # Conversation history
                for message in st.session_state.floating_messages:

                    with st.chat_message(message["role"]):
                        st.markdown(message["content"])

                # Chat input
                with st.form("floating_ai_form", clear_on_submit=True):

                    question = st.text_input(
                        "Ask about your financial data",
                        placeholder="e.g. Which product has highest revenue?"
                    )

                    submitted = st.form_submit_button("Send")

                if submitted and question.strip():

                    st.session_state.floating_messages.append({
                        "role": "user",
                        "content": question
                    })

                    with st.spinner("Analyzing your financial data..."):

                        response = ask_agent(dataset_id, question)

                    if response and response.get("status") == "success":

                        result = response.get("result", {})

                        answer = result.get(
                            "answer",
                            "No answer was returned."
                        )

                        st.session_state.floating_messages.append({
                            "role": "assistant",
                            "content": answer
                        })

                    else:

                        error = (
                            response.get("error", "AI request failed.")
                            if response else
                            "Unable to connect to the backend."
                        )

                        st.session_state.floating_messages.append({
                            "role": "assistant",
                            "content": f"Error: {error}"
                        })

                    st.rerun()

                if st.session_state.floating_messages:

                    if st.button(
                        "Clear Chat",
                        key="clear_floating_chat"
                    ):
                        st.session_state.floating_messages = []
                        st.rerun()
