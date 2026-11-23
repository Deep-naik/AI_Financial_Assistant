
from app.agents.rag_agent import RAGAgent


agent = RAGAgent()

questions = [
    "Which business segment is making losses?",
    "Which product generates the highest revenue?",
    "Which country has the highest profit?"
]

for question in questions:

    print("\n" + "=" * 70)
    print("QUESTION:", question)

    try:
        result = agent.run(question)

        print("AGENT:", result["agent"])
        print("ANALYSIS TYPE:", result["analysis_type"])

        print("\nANSWER:")
        print(result["result"]["answer"])

        print("\nRETRIEVED SOURCES:")
        for source in result["result"]["sources"]:
            print(
                source["id"],
                "|",
                source["name"],
                "|",
                source["category"]
            )

    except Exception as error:
        print("ERROR:", error)
