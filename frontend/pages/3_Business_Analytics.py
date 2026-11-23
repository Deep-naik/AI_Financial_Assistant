
import streamlit as st
import pandas as pd

from utils.api import fetch_analytics
from utils.common import (
    initialize_session,
    show_dataset_selector,
    render_floating_assistant
)

st.set_page_config(
    page_title="Business Analytics",
    page_icon="📈",
    layout="wide"
)

initialize_session()

st.title("📈 Business Analytics")
st.caption(
    "Explore product, country and segment performance, "
    "profitability diagnostics and financial anomalies."
)

dataset_id = show_dataset_selector()

if not dataset_id:
    st.stop()

st.markdown("---")

# --------------------------------------------------
# DIMENSION ANALYSIS
# --------------------------------------------------

st.header("1. Dimension-wise Performance Analysis")

dimension = st.selectbox(
    "Choose Analysis Dimension",
    ["product", "country", "segment"]
)

breakdown = fetch_analytics(
    "breakdown",
    dataset_id,
    dimension=dimension
)

if breakdown and breakdown.get("status") == "success":

    analysis = breakdown["analysis"]

    results = analysis["results"]

    df = pd.DataFrame(results)

    if not df.empty:

        col1, col2 = st.columns(2)

        col1.metric(
            "Total Categories",
            analysis["total_categories"]
        )

        highest = analysis["highest_revenue"]

        col2.metric(
            "Highest Revenue Category",
            highest["name"],
            f"{highest['revenue']:,.2f}"
        )

        st.subheader(
            f"{dimension.title()}-wise Revenue"
        )

        st.bar_chart(
            df.set_index("name")["revenue"]
        )

        st.subheader(
            f"{dimension.title()}-wise Profit"
        )

        st.bar_chart(
            df.set_index("name")["profit"]
        )

        st.subheader("Profit Margin Comparison")

        st.bar_chart(
            df.set_index("name")[
                "profit_margin_percentage"
            ]
        )

        st.subheader("Detailed Performance Table")

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

    else:
        st.info("No dimension analysis available.")

else:
    st.error("Unable to retrieve dimension analysis.")

st.markdown("---")

# --------------------------------------------------
# PROFITABILITY DIAGNOSTICS
# --------------------------------------------------

st.header("2. Profitability Diagnostics")

diagnostic_dimension = st.selectbox(
    "Choose Diagnostic Dimension",
    ["segment", "product", "country"]
)

diagnostics = fetch_analytics(
    "diagnostics",
    dataset_id,
    dimension=diagnostic_dimension
)

if diagnostics and diagnostics.get("status") == "success":

    diagnostic_data = diagnostics["diagnostics"]

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Overall Profit Margin",
        f"{diagnostic_data['overall_profit_margin']:.2f}%"
    )

    col2.metric(
        "Total Revenue",
        f"{diagnostic_data['total_revenue']:,.2f}"
    )

    col3.metric(
        "Total Profit",
        f"{diagnostic_data['total_profit']:,.2f}"
    )

    category_data = pd.DataFrame(
        diagnostic_data["category_analysis"]
    )

    st.subheader("Category Profitability")

    st.bar_chart(
        category_data.set_index("name")[
            "profit_margin_percentage"
        ]
    )

    st.subheader("Diagnostic Findings")

    findings = diagnostic_data.get(
        "diagnostic_findings",
        []
    )

    if findings:

        for finding in findings:

            severity = finding["severity"].upper()

            message = (
                f"**{finding['category']} — "
                f"{finding['finding']}**\n\n"
                f"{finding['details']}"
            )

            if severity == "HIGH":
                st.error(message)

            elif severity == "MEDIUM":
                st.warning(message)

            else:
                st.info(message)

    st.subheader("Detailed Diagnostic Table")

    st.dataframe(
        category_data,
        use_container_width=True,
        hide_index=True
    )

else:
    st.error("Unable to retrieve profitability diagnostics.")

st.markdown("---")

# --------------------------------------------------
# ANOMALY DETECTION
# --------------------------------------------------

st.header("3. Financial Anomaly Detection")

anomaly_response = fetch_analytics(
    "anomalies",
    dataset_id
)

if (
    anomaly_response
    and anomaly_response.get("status") == "success"
):

    anomaly_data = anomaly_response["anomaly_analysis"]

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Total Records",
        anomaly_data["total_records"]
    )

    col2.metric(
        "Total Anomalies",
        anomaly_data["total_anomalies"]
    )

    col3.metric(
        "Negative Profit Records",
        anomaly_data["negative_profit_records"]
    )

    st.subheader("Statistical Outliers")

    outliers = anomaly_data["statistical_outliers"]

    outlier_df = pd.DataFrame(
        {
            "Metric": list(outliers.keys()),
            "Outlier Count": list(outliers.values())
        }
    )

    col1, col2 = st.columns(2)

    with col1:
        st.bar_chart(
            outlier_df.set_index("Metric")
        )

    with col2:
        st.dataframe(
            outlier_df,
            use_container_width=True,
            hide_index=True
        )

    st.subheader("Detected Anomaly Records")

    anomaly_records = pd.DataFrame(
        anomaly_data["anomaly_records"]
    )

    if not anomaly_records.empty:

        anomaly_types = sorted(
            anomaly_records["anomaly_type"].unique()
        )

        selected_types = st.multiselect(
            "Filter by Anomaly Type",
            anomaly_types,
            default=anomaly_types
        )

        filtered_df = anomaly_records[
            anomaly_records["anomaly_type"].isin(
                selected_types
            )
        ]

        st.dataframe(
            filtered_df,
            use_container_width=True,
            hide_index=True
        )

        st.download_button(
            "Download Anomaly Records",
            data=filtered_df.to_csv(index=False),
            file_name="financial_anomalies.csv",
            mime="text/csv"
        )

    else:
        st.info("No anomaly records detected.")

else:
    st.error("Unable to retrieve anomaly analysis.")

st.caption(
    "Anomaly flags indicate statistical outliers or negative-profit "
    "records. They should be investigated, not automatically treated "
    "as data errors."
)

render_floating_assistant()