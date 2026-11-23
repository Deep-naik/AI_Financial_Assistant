
import streamlit as st
from utils.common import render_floating_assistant
from utils.api import check_backend
from utils.common import (
    initialize_session,
    show_dataset_selector
)

st.set_page_config(
    page_title="AI Financial Intelligence",
    page_icon="📊",
    layout="wide"
)

initialize_session()

st.title("📊 AI Financial Intelligence")
st.caption("AI-Powered Business Intelligence & Decision Support Assistant")

st.markdown("---")

# Backend status
if check_backend():
    st.success("Backend connected successfully")
else:
    st.error("Backend is unavailable. Please start the FastAPI server.")

st.header("Welcome")

st.write(
    """
    Analyze financial performance, discover business insights,
    forecast future trends, and interact with an AI-powered
    financial intelligence assistant.
    """
)

st.subheader("Select Your Dataset")

dataset_id = show_dataset_selector()

if dataset_id:
    st.success("Dataset selected successfully.")

st.markdown("---")

st.subheader("Explore the Application")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📈 Financial Analysis")
    st.write(
        "Explore financial KPIs, revenue, profit, "
        "product performance, and country-wise analysis."
    )

    st.markdown("### 🔮 Financial Forecasting")
    st.write(
        "Generate revenue and profit forecasts "
        "using predictive models."
    )

with col2:
    st.markdown("### 🤖 AI Assistant")
    st.write(
        "Ask questions about your financial dataset "
        "using the multi-agent AI system."
    )

    st.markdown("### 📄 Financial Reports")
    st.write(
        "Generate and download comprehensive PDF reports."
    )

st.markdown("---")

st.caption("AI Financial Intelligence | MSc Data Science Project")

render_floating_assistant()