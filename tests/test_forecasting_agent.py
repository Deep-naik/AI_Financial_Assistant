
import pandas as pd

from app.agents.forecasting_agent import ForecastingAgent


df = pd.read_csv(
    "data/processed/financial_sample_cleaned.csv"
)

agent = ForecastingAgent()

questions = [
    "Forecast revenue and profit for the next three months",
    "Forecast revenue for the next six months"
]

for question in questions:

    print("\n" + "=" * 70)
    print("QUESTION:", question)

    try:
        result = agent.run(df, question)

        print("AGENT:", result["agent"])
        print("ANALYSIS TYPE:", result["analysis_type"])
        print("FORECAST PERIODS:", result["forecast_periods"])

        print("\nFORECAST RESULTS:")
        print(result["result"])

    except Exception as error:
        print("ERROR:", error)
