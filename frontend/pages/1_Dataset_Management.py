
import streamlit as st
import pandas as pd
import requests

from utils.api import API_URL, fetch_datasets
from utils.common import (
    initialize_session,
    show_dataset_selector,
    render_floating_assistant
)

st.set_page_config(
    page_title="Dataset Management",
    page_icon="📁",
    layout="wide"
)

initialize_session()

st.title("📁 Dataset Management")
st.caption("Upload, view and manage financial datasets")

st.markdown("---")

# Dataset selection
st.subheader("Select Active Dataset")

selected_id = show_dataset_selector()

st.markdown("---")

# Upload dataset
st.subheader("Upload a New Dataset")

uploaded_file = st.file_uploader(
    "Choose a CSV or Excel file",
    type=["csv", "xlsx"]
)

if uploaded_file is not None:

    if st.button("Upload Dataset", type="primary"):

        try:
            response = requests.post(
                f"{API_URL}/api/data/upload",
                files={
                    "file": (
                        uploaded_file.name,
                        uploaded_file.getvalue(),
                        uploaded_file.type
                    )
                },
                timeout=180
            )

            if response.status_code in [200, 201]:

                result = response.json()

                st.success("Dataset uploaded successfully!")

                st.session_state.dataset_id = result.get(
                    "dataset_id",
                    st.session_state.dataset_id
                )

                st.rerun()

            else:
                st.error(
                    f"Upload failed: {response.status_code}"
                )
                st.code(response.text)

        except requests.RequestException as error:
            st.error(f"Connection error: {error}")

st.markdown("---")

# Available datasets

# Available datasets
st.subheader("Available Datasets")

datasets = fetch_datasets()

if datasets:

    st.metric("Total Uploaded Datasets", len(datasets))

    for index, dataset in enumerate(datasets):

        col1, col2, col3, col4, col5, col6 = st.columns(
            [3, 1, 1, 1.5, 2.5, 0.7]
        )

        with col1:
            st.write(f"**{dataset['filename']}**")

        with col2:
            st.write(f"{dataset['total_rows']}")

        with col3:
            st.write(f"{dataset['total_columns']}")

        with col4:
            st.write(dataset["status"])

        with col5:
            st.caption(dataset["upload_date"])

        with col6:
            if st.button(
                "🗑️",
                key=f"delete_{dataset['dataset_id']}",
                help="Delete this dataset"
            ):
                st.session_state.delete_dataset_id = dataset["dataset_id"]
                st.session_state.delete_dataset_name = dataset["filename"]

        st.divider()

    # Deletion confirmation
    if st.session_state.get("delete_dataset_id"):

        delete_id = st.session_state.delete_dataset_id
        delete_name = st.session_state.delete_dataset_name

        st.warning(
            f"Are you sure you want to delete **{delete_name}**? "
            "This action cannot be undone."
        )

        confirm_col, cancel_col = st.columns(2)

        with confirm_col:
            if st.button("Yes, Delete", type="primary"):

                try:
                    response = requests.delete(
                        f"{API_URL}/api/data/datasets/{delete_id}",
                        timeout=30
                    )

                    if response.status_code == 200:

                        st.success("Dataset deleted successfully!")

                        if st.session_state.dataset_id == delete_id:
                            st.session_state.dataset_id = None

                        del st.session_state.delete_dataset_id
                        del st.session_state.delete_dataset_name

                        st.rerun()

                    else:
                        st.error(f"Deletion failed: {response.text}")

                except requests.RequestException as error:
                    st.error(f"Connection error: {error}")

        with cancel_col:
            if st.button("Cancel"):
                del st.session_state.delete_dataset_id
                del st.session_state.delete_dataset_name
                st.rerun()

else:
    st.info("No datasets available. Upload a dataset to begin.")
render_floating_assistant()