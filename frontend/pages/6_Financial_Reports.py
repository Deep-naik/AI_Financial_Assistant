
import streamlit as st

from utils.api import download_report
from utils.common import (
    initialize_session,
    show_dataset_selector
)


st.set_page_config(
    page_title="Financial Reports",
    page_icon="📄",
    layout="wide"
)

initialize_session()

st.title("📄 Financial Reports")
st.caption(
    "Generate and download a comprehensive financial intelligence report."
)

dataset_id = show_dataset_selector()

if not dataset_id:
    st.warning("Please upload or select a dataset first.")
    st.stop()

st.divider()

st.subheader("Financial Intelligence Report")

st.markdown(
    """
    Your PDF report includes:

    1. **Executive Financial Summary**
       - Total sales, profit, COGS and discounts
       - Profit margin and profitability overview

    2. **Business Dimension Analysis**
       - Product-wise performance
       - Country-wise performance
       - Segment-wise performance

    3. **Financial Trends**
       - Monthly revenue and profit analysis
       - Quarterly performance analysis

    4. **Predictive Analytics**
       - Three-month revenue forecast
       - Three-month profit forecast
       - Forecast model evaluation metrics
    """
)

st.info(
    "The report is generated using the selected dataset. "
    "All financial values use the dataset's currency units."
)

st.divider()

st.subheader("Download Report")

st.write(
    "Click the button below to generate and download your "
    "financial intelligence report in PDF format."
)

if st.button("Generate PDF Report", type="primary"):
    with st.spinner("Generating your financial report..."):
        report_bytes = download_report(dataset_id)

    if report_bytes:
        st.success("Your financial report is ready!")

        st.download_button(
            label="📥 Download Financial Report",
            data=report_bytes,
            file_name="financial_intelligence_report.pdf",
            mime="application/pdf"
        )
    else:
        st.error(
            "Unable to generate the report. "
            "Please check whether the backend is running."
        )

st.divider()

st.caption(
    "Report generation is handled by the FastAPI backend "
    "using the ReportLab PDF generation service."
)

render_floating_assistant()