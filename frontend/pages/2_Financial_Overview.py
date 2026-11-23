
import streamlit as st
import pandas as pd

from utils.api import fetch_analytics
from utils.common import (
    initialize_session,
    show_dataset_selector,
    render_floating_assistant
)

st.set_page_config(
    page_title="Financial Overview",
    page_icon="📊",
    layout="wide"
)

initialize_session()

st.title("📊 Financial Overview")
st.caption("Key financial performance indicators")

dataset_id = show_dataset_selector()

if not dataset_id:
    st.stop()

st.markdown("---")

# Financial KPIs
st.subheader("Financial Performance")

response = fetch_analytics("kpis", dataset_id)

if response and response.get("status") == "success":

    analytics = response["analytics"]
    kpis = analytics["financial_kpis"]
    averages = analytics["averages"]
    profitability = analytics["profitability"]

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Sales", f"{kpis['total_sales']:,.2f}")
    col2.metric("Total Profit", f"{kpis['total_profit']:,.2f}")
    col3.metric("Profit Margin", f"{kpis['profit_margin_percentage']:.2f}%")
    col4.metric("Units Sold", f"{kpis['total_units_sold']:,.0f}")

    col1, col2, col3 = st.columns(3)

    col1.metric("Total COGS", f"{kpis['total_cogs']:,.2f}")
    col2.metric("Total Discounts", f"{kpis['total_discounts']:,.2f}")
    col3.metric(
        "Average Sales per Record",
        f"{averages['average_sales_per_record']:,.2f}"
    )

    st.markdown("### Record Profitability")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Profitable Records",
        profitability["profitable_records"]
    )

    col2.metric(
        "Loss-Making Records",
        profitability["loss_making_records"]
    )

    col3.metric(
        "Zero-Profit Records",
        profitability["zero_profit_records"]
    )

else:
    st.error("Unable to retrieve KPI data.")

st.markdown("---")

# Monthly Trends
st.subheader("Monthly Revenue and Profit Trends")

trend_response = fetch_analytics("trends", dataset_id)

if trend_response and trend_response.get("status") == "success":

    monthly_data = trend_response[
        "monthly_analysis"
    ]["monthly_trends"]

    df = pd.DataFrame(monthly_data)

    if not df.empty:

        df["month"] = pd.to_datetime(df["month"])

        df = df.sort_values("month")

        chart_data = df.set_index("month")[
            ["revenue", "profit"]
        ]

        st.markdown("### Revenue and Profit")

        st.line_chart(chart_data)

        col1, col2 = st.columns(2)

        best_month = trend_response[
            "monthly_analysis"
        ]["best_revenue_month"]

        worst_month = trend_response[
            "monthly_analysis"
        ]["worst_revenue_month"]

        col1.metric(
            "Highest Revenue Month",
            best_month["month"],
            f"{best_month['revenue']:,.2f}"
        )

        col2.metric(
            "Lowest Revenue Month",
            worst_month["month"],
            f"{worst_month['revenue']:,.2f}"
        )

        st.markdown("### Monthly Financial Details")

        display_df = df.copy()
        display_df["month"] = display_df["month"].dt.strftime("%Y-%m")

        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )

    else:
        st.info("No monthly trend data available.")

else:
    st.error("Unable to retrieve monthly trends.")

st.markdown("---")

# Quarterly Analysis
st.subheader("Quarterly Financial Performance")

if trend_response and trend_response.get("status") == "success":

    quarterly_data = trend_response.get(
        "quarterly_analysis",
        []
    )

    if quarterly_data:

        quarterly_df = pd.DataFrame(quarterly_data)

        st.bar_chart(
            quarterly_df.set_index("quarter")[
                ["revenue", "profit"]
            ]
        )

        st.dataframe(
            quarterly_df,
            use_container_width=True,
            hide_index=True
        )

st.caption(
    "Financial values are expressed in the dataset's currency units. "
    "The dataset contains historical records from September 2013 "
    "to December 2014."
)
render_floating_assistant()