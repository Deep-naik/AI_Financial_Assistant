
import pandas as pd

from app.agents.agent_orchestrator import AgentOrchestrator


df = pd.read_csv(
    "data/processed/financial_sample_cleaned.csv"
)

orchestrator = AgentOrchestrator()

questions = [
    "Show me the overall financial KPIs",
    "Forecast revenue for the next three months",
    "Which product generates the highest revenue?",
    "Show the quarterly financial trends",
    "Which business segment is making losses?"
]

for question in questions:

    print("\n" + "=" * 70)
    print("QUESTION:", question)

    try:
        result = orchestrator.run(df, question)

        print("SELECTED AGENT:", result["agent"])
        print("ANALYSIS TYPE:", result["analysis_type"])

        if result["agent"] == "rag":
            print("\nANSWER:")
            print(result["result"]["answer"])

        elif result["agent"] == "forecasting":
            print("\nFORECAST RESULTS:")
            print(result["result"])

        else:
            print("\nANALYTICS RESULTS:")
            print(result["result"])

    except Exception as error:
        print("ERROR:", error)
