
import streamlit as st
import pandas as pd

from utils.api import fetch_analytics
from utils.common import (
    initialize_session,
    show_dataset_selector,
    render_floating_assistant
)


st.set_page_config(
    page_title="Financial Forecasting",
    page_icon="🔮",
    layout="wide"
)

initialize_session()

st.title("🔮 Financial Forecasting")
st.caption(
    "Predict future revenue and profit using statistical forecasting models."
)

dataset_id = show_dataset_selector()

if not dataset_id:
    st.warning("Please upload or select a dataset first.")
    st.stop()

st.divider()

# Forecast horizon
st.subheader("Forecast Configuration")

periods = st.selectbox(
    "Select Forecast Horizon",
    options=[3, 6, 12],
    format_func=lambda x: f"{x} Months"
)

if st.button("Generate Forecast", type="primary"):
    st.session_state["forecast_periods"] = periods
    st.session_state["run_forecast"] = True

if "run_forecast" not in st.session_state:
    st.info("Select a forecast horizon and click Generate Forecast.")
    st.stop()

if st.session_state.get("forecast_periods") != periods:
    st.info("Click Generate Forecast to apply the new forecast horizon.")
    st.stop()

with st.spinner("Generating financial forecasts..."):
    response = fetch_analytics(
        "forecast",
        dataset_id,
        periods=periods
    )

if not response or response.get("status") != "success":
    st.error("Unable to generate forecasts. Check the backend.")
    st.stop()

forecast_data = response["forecast_analysis"]

revenue = forecast_data["revenue_forecast"]
profit = forecast_data["profit_forecast"]

st.divider()

# Forecast summary
st.subheader("Forecast Summary")

col1, col2, col3 = st.columns(3)

col1.metric(
    "Historical Months",
    forecast_data["historical_months"]
)

col2.metric(
    "Forecast Period",
    f'{forecast_data["forecast_periods"]} Months'
)

col3.metric(
    "Model Selection",
    revenue["selected_model"]
)

st.caption(
    "The model is selected using the lowest Mean Absolute Error (MAE) "
    "on a common holdout test set."
)

st.divider()

# Revenue forecast
st.subheader("Revenue Forecast")

revenue_df = pd.DataFrame(revenue["forecast"])

col1, col2, col3 = st.columns(3)

col1.metric("Selected Model", revenue["selected_model"])
col2.metric("MAE", f'{revenue["evaluation"]["mae"]:,.2f}')
col3.metric(
    "MAPE",
    f'{revenue["evaluation"]["mape_percentage"]:.2f}%'
)

st.line_chart(
    revenue_df.set_index("month")["predicted_value"],
    y_label="Predicted Revenue"
)

st.dataframe(
    revenue_df.rename(
        columns={
            "month": "Month",
            "predicted_value": "Predicted Revenue"
        }
    ),
    use_container_width=True,
    hide_index=True
)

# Revenue model comparison
with st.expander("Revenue Model Comparison"):
    comparison = pd.DataFrame(
        revenue["model_comparison"]
    ).T

    comparison.index = [
        name.replace("_", " ").title()
        for name in comparison.index
    ]

    comparison.index.name = "Model"

    st.dataframe(
        comparison,
        use_container_width=True
    )

st.divider()

# Profit forecast
st.subheader("Profit Forecast")

profit_df = pd.DataFrame(profit["forecast"])

col1, col2, col3 = st.columns(3)

col1.metric("Selected Model", profit["selected_model"])
col2.metric("MAE", f'{profit["evaluation"]["mae"]:,.2f}')
col3.metric(
    "MAPE",
    f'{profit["evaluation"]["mape_percentage"]:.2f}%'
)

st.line_chart(
    profit_df.set_index("month")["predicted_value"],
    y_label="Predicted Profit"
)

st.dataframe(
    profit_df.rename(
        columns={
            "month": "Month",
            "predicted_value": "Predicted Profit"
        }
    ),
    use_container_width=True,
    hide_index=True
)

# Profit model comparison
with st.expander("Profit Model Comparison"):
    comparison = pd.DataFrame(
        profit["model_comparison"]
    ).T

    comparison.index = [
        name.replace("_", " ").title()
        for name in comparison.index
    ]

    comparison.index.name = "Model"

    st.dataframe(
        comparison,
        use_container_width=True
    )

st.divider()

# Interpretation
st.subheader("Forecast Interpretation")

st.markdown(
    f"""
    - **Revenue:** The {revenue["selected_model"]} model was selected.
      Its MAPE is {revenue["evaluation"]["mape_percentage"]:.2f}%.
    - **Profit:** The {profit["selected_model"]} model was selected.
      Its MAPE is {profit["evaluation"]["mape_percentage"]:.2f}%.
    - The model selection method is based on the lowest MAE among
      Naive, Holt and Seasonal Naive models.
    """
)

st.warning(
    "These forecasts extend the historical dataset. They are not "
    "predictions for the current year. Forecast accuracy is limited "
    "by the available historical observations."
)

st.caption(
    "All financial values are expressed in the dataset's currency units."
)

render_floating_assistant()