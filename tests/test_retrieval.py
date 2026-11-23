
from app.rag.retrieval import FinancialRetriever


retriever = FinancialRetriever()

query = "Which business segment is making losses?"

results = retriever.retrieve(
    query=query,
    n_results=3
)

print("\nRAG RETRIEVAL RESULTS")
print("User Query:", query)

for index, result in enumerate(results, start=1):

    print(f"\nResult {index}")
    print("ID:", result["id"])
    print("Category:", result["metadata"]["category"])
    print("Name:", result["metadata"]["name"])
    print("Distance:", result["distance"])
    print("Document:", result["document"])
