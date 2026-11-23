
import streamlit as st
import requests
import pandas as pd

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="AI Financial Intelligence",
    page_icon="📊",
    layout="wide"
)

API_URL = "http://127.0.0.1:8000"


# --------------------------------------------------
# PAGE HEADER
# --------------------------------------------------

st.title("📊 AI-Powered Financial Intelligence")
st.caption(
    "Business Intelligence and Decision Support Assistant"
)

st.divider()


# --------------------------------------------------
# BACKEND CONNECTION
# --------------------------------------------------

def check_backend():

    try:
        response = requests.get(
            f"{API_URL}/",
            timeout=5
        )

        return response.status_code == 200

    except requests.RequestException:
        return False


# --------------------------------------------------
# FETCH DATASETS
# --------------------------------------------------

def fetch_datasets():

    try:
        response = requests.get(
            f"{API_URL}/api/data/datasets",
            timeout=10
        )

        response.raise_for_status()

        return response.json()

    except requests.RequestException as error:
        st.error(f"Unable to fetch datasets: {error}")
        return None


# --------------------------------------------------
# ASK AI AGENT
# --------------------------------------------------


def ask_agent(dataset_id, question):

    try:
        response = requests.post(
            f"{API_URL}/api/agents/ask",
            json={
                "dataset_id": dataset_id,
                "question": question
            },
            timeout=180
        )

        if not response.ok:
            st.error(f"HTTP Status: {response.status_code}")
            st.error(f"API Response: {response.text}")
            return None

        return response.json()

    except requests.RequestException as error:
        st.error(f"Connection error: {error}")
        return None


# --------------------------------------------------
# FETCH FINANCIAL ANALYTICS
# --------------------------------------------------

def fetch_analytics(endpoint, dataset_id):

    try:
        response = requests.get(
            f"{API_URL}/api/analytics/{endpoint}",
            params={"dataset_id": dataset_id},
            timeout=30
        )

        response.raise_for_status()

        return response.json()

    except requests.RequestException as error:
        st.error(f"Analytics request failed: {error}")
        return None

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

st.sidebar.title("⚙️ Configuration")

if check_backend():
    st.sidebar.success("Backend Connected")
else:
    st.sidebar.error("Backend Disconnected")

st.sidebar.markdown("---")
st.sidebar.write("**Available Modules**")
st.sidebar.write("📈 Financial Analytics")
st.sidebar.write("🔮 Forecasting")
st.sidebar.write("🤖 AI Assistant")
st.sidebar.write("📚 Knowledge Retrieval")


# --------------------------------------------------
# DATASET SELECTION
# --------------------------------------------------

st.header("Dataset Selection")

datasets_response = fetch_datasets()

dataset_id = None

if datasets_response:

    datasets = datasets_response

    if isinstance(datasets_response, dict):
        datasets = datasets_response.get(
            "datasets",
            datasets_response.get("data", [])
        )

    if datasets:

        dataset_options = {
            item["dataset_id"]: item
            for item in datasets
        }

        selected_id = st.selectbox(
            "Select Financial Dataset",
            options=list(dataset_options.keys()),
            format_func=lambda value: (
                dataset_options[value].get("filename")
                or dataset_options[value].get("name")
                or value
            )
        )

        dataset_id = selected_id

    else:
        st.warning("No datasets available. Upload a dataset first.")

else:
    st.warning("Could not retrieve datasets from the backend.")


st.divider()


# --------------------------------------------------
# FINANCIAL KPI DASHBOARD
# --------------------------------------------------

if dataset_id:

    st.header("📊 Financial Performance Dashboard")

    kpi_response = fetch_analytics(
        "kpis",
        dataset_id
    )

    if kpi_response:

        analytics = kpi_response["analytics"]
        financial = analytics["financial_kpis"]
        profitability = analytics["profitability"]

        st.subheader("Key Financial Indicators")

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Total Revenue",
            f"{financial['total_sales']:,.2f}"
        )

        col2.metric(
            "Total Profit",
            f"{financial['total_profit']:,.2f}"
        )

        col3.metric(
            "Profit Margin",
            f"{financial['profit_margin_percentage']:.2f}%"
        )

        col4, col5, col6 = st.columns(3)

        col4.metric(
            "Total COGS",
            f"{financial['total_cogs']:,.2f}"
        )

        col5.metric(
            "Total Discounts",
            f"{financial['total_discounts']:,.2f}"
        )

        col6.metric(
            "Units Sold",
            f"{financial['total_units_sold']:,.0f}"
        )

        st.subheader("Record Profitability")

        p1, p2, p3 = st.columns(3)

        p1.metric(
            "Profitable Records",
            profitability["profitable_records"]
        )

        p2.metric(
            "Loss-Making Records",
            profitability["loss_making_records"]
        )

        p3.metric(
            "Zero-Profit Records",
            profitability["zero_profit_records"]
        )

    st.divider()



# --------------------------------------------------
# MONTHLY FINANCIAL TRENDS
# --------------------------------------------------

if dataset_id:

    st.subheader("📈 Monthly Revenue and Profit Trends")

    trends_response = fetch_analytics(
        "trends",
        dataset_id
    )

    if trends_response:

        monthly_data = trends_response[
            "monthly_analysis"
        ]["monthly_trends"]

        monthly_df = pd.DataFrame(monthly_data)

        if not monthly_df.empty:

            monthly_df["month"] = pd.to_datetime(
                monthly_df["month"]
            )

            monthly_df = monthly_df.sort_values("month")

            monthly_df["month_label"] = (
                monthly_df["month"].dt.strftime("%b %Y")
            )

            col1, col2 = st.columns(2)

            with col1:

                st.markdown("**Monthly Revenue**")

                revenue_chart = monthly_df.set_index(
                    "month_label"
                )[["revenue"]]

                st.line_chart(
                    revenue_chart,
                    y="revenue",
                    use_container_width=True
                )

            with col2:

                st.markdown("**Monthly Profit**")

                profit_chart = monthly_df.set_index(
                    "month_label"
                )[["profit"]]

                st.line_chart(
                    profit_chart,
                    y="profit",
                    use_container_width=True
                )

            with st.expander("View Monthly Financial Data"):

                st.dataframe(
                    monthly_df[
                        [
                            "month_label",
                            "revenue",
                            "profit",
                            "expenses",
                            "discounts"
                        ]
                    ],
                    use_container_width=True
                )

            # Highlight best and worst revenue months
            best_month = trends_response[
                "monthly_analysis"
            ]["best_revenue_month"]

            worst_month = trends_response[
                "monthly_analysis"
            ]["worst_revenue_month"]

            st.subheader("Revenue Highlights")

            h1, h2 = st.columns(2)

            h1.metric(
                "Highest Revenue Month",
                best_month["month"],
                f"{best_month['revenue']:,.2f}"
            )

            h2.metric(
                "Lowest Revenue Month",
                worst_month["month"],
                f"{worst_month['revenue']:,.2f}"
            )

    st.divider()



# --------------------------------------------------
# BUSINESS DIMENSION ANALYSIS
# --------------------------------------------------

if dataset_id:

    st.header("🌍 Business Performance Analysis")

    dimension = st.selectbox(
        "Choose Analysis Dimension",
        ["product", "country", "segment"]
    )

    breakdown_response = requests.get(
        f"{API_URL}/api/analytics/breakdown",
        params={
            "dataset_id": dataset_id,
            "dimension": dimension
        },
        timeout=30
    )

    if breakdown_response.status_code == 200:

        breakdown = breakdown_response.json()["analysis"]

        dimension_df = pd.DataFrame(
            breakdown["results"]
        )

        st.subheader(
            f"{dimension.title()} Performance"
        )

        col1, col2 = st.columns(2)

        with col1:

            st.markdown("**Revenue by Category**")

            revenue_df = dimension_df[
                ["name", "revenue"]
            ].set_index("name")

            st.bar_chart(revenue_df)

        with col2:

            st.markdown("**Profit by Category**")

            profit_df = dimension_df[
                ["name", "profit"]
            ].set_index("name")

            st.bar_chart(profit_df)

        st.subheader("Detailed Performance")

        st.dataframe(
            dimension_df,
            use_container_width=True
        )

    else:

        st.error(
            f"Unable to load dimension analysis: "
            f"{breakdown_response.text}"
        )

    st.divider()


# --------------------------------------------------
# FINANCIAL FORECASTING DASHBOARD
# --------------------------------------------------

if dataset_id:

    st.header("🔮 Financial Forecasting")

    forecast_periods = st.selectbox(
        "Select Forecast Period",
        [3, 6, 12],
        format_func=lambda x: f"{x} Months"
    )

    if st.button("Generate Forecast"):

        with st.spinner("Generating financial forecasts..."):

            try:

                response = requests.get(
                    f"{API_URL}/api/analytics/forecast",
                    params={
                        "dataset_id": dataset_id,
                        "periods": forecast_periods
                    },
                    timeout=60
                )

                response.raise_for_status()

                forecast_data = response.json()[
                    "forecast_analysis"
                ]

                st.success("Forecast generated successfully!")

                revenue = forecast_data["revenue_forecast"]
                profit = forecast_data["profit_forecast"]

                # Revenue forecast
                st.subheader("Revenue Forecast")

                revenue_df = pd.DataFrame(
                    revenue["forecast"]
                )

                revenue_df = revenue_df.set_index("month")

                st.line_chart(
                    revenue_df,
                    y="predicted_value",
                    use_container_width=True
                )

                st.write(
                    "Selected Model:",
                    revenue["selected_model"]
                )

                # Profit forecast
                st.subheader("Profit Forecast")

                profit_df = pd.DataFrame(
                    profit["forecast"]
                )

                profit_df = profit_df.set_index("month")

                st.line_chart(
                    profit_df,
                    y="predicted_value",
                    use_container_width=True
                )

                st.write(
                    "Selected Model:",
                    profit["selected_model"]
                )

                
                # --------------------------------
                # Model Evaluation and Comparison
                # --------------------------------

                st.subheader("Model Evaluation")

                col1, col2 = st.columns(2)

                with col1:

                    st.markdown("### Revenue Model")

                    st.write("Selected Model:", revenue["selected_model"])

                    st.json(revenue["evaluation"])

                    revenue_comparison = pd.DataFrame(
                        revenue["model_comparison"]
                    ).T

                    st.markdown("**Model Comparison**")
                    st.dataframe(
                        revenue_comparison,
                        use_container_width=True
                    )

                with col2:

                    st.markdown("### Profit Model")

                    st.write("Selected Model:", profit["selected_model"])

                    st.json(profit["evaluation"])

                    profit_comparison = pd.DataFrame(
                        profit["model_comparison"]
                    ).T

                    st.markdown("**Model Comparison**")
                    st.dataframe(
                        profit_comparison,
                        use_container_width=True
                    )


            except requests.RequestException as error:

                st.error(
                    f"Forecast request failed: {error}"
                )

    st.divider()


# --------------------------------------------------
# AI QUESTION AND ANSWER
# --------------------------------------------------

st.header("🤖 Ask Your Financial AI Assistant")

st.write(
    "Ask questions about financial performance, "
    "products, countries, segments, anomalies or forecasts."
)

question = st.text_area(
    "Enter your financial question",
    placeholder="Example: Which business segment is making losses?"
)

if st.button("Submit Question", type="primary"):

    if not dataset_id:
        st.warning("Please select a dataset.")

    elif not question.strip():
        st.warning("Please enter a question.")

    else:

        with st.spinner("AI agents are analysing your question..."):

            result = ask_agent(
                dataset_id,
                question
            )

        if result:

            st.success("Analysis completed successfully!")

            st.subheader("Selected Agent")

            st.info(
                result.get("agent", "Unknown").upper()
            )

            st.write(
                "Analysis Type:",
                result.get("analysis_type")
            )

            st.subheader("Result")

            agent_result = result.get("result", {})

            if result.get("agent") == "rag":

                st.markdown(
                    agent_result.get("answer", "No answer returned.")
                )

                sources = agent_result.get("sources", [])

                if sources:

                    with st.expander("View Retrieved Sources"):

                        st.dataframe(
                            pd.DataFrame(sources),
                            use_container_width=True
                        )

            else:

                st.json(agent_result)


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()

st.caption(
    "AI-Powered Business Intelligence & Decision Support System"
)
