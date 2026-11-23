
import pandas as pd

from app.agents.analytics_agent import AnalyticsAgent


df = pd.read_csv(
    "data/processed/financial_sample_cleaned.csv"
)

agent = AnalyticsAgent()

questions = [
    "Show overall financial performance",
    "Which product has the highest revenue?",
    "Show quarterly trends",
    "Identify financial anomalies",
    "Diagnose why a segment is making losses"
]

for question in questions:

    print("\n" + "=" * 70)
    print("QUESTION:", question)

    try:
        result = agent.run(df, question)

        print("AGENT:", result["agent"])
        print("ANALYSIS TYPE:", result["analysis_type"])
        print("RESULT:")
        print(result["result"])

    except Exception as error:
        print("ERROR:", error)
