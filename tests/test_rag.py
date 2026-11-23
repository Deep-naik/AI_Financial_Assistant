
from app.services.rag_service import FinancialRAGService


rag = FinancialRAGService()

questions = [
    "Which business segment is making losses?",
    "Which product generates the highest revenue?",
    "Which country has the highest profit?"
]

for question in questions:

    print("\n" + "=" * 70)
    print("QUESTION:", question)

    result = rag.ask_question(
        question=question,
        n_results=5
    )

    print("\nGROQ ANSWER:")
    print(result["answer"])

    print("\nRETRIEVED SOURCES:")

    for source in result["sources"]:
        print(
            source["category"],
            "|",
            source["name"],
            "| Distance:",
            round(source["distance"], 4)
        )
