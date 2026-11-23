
from app.rag.vector_store import FinancialVectorStore


vector_store = FinancialVectorStore()

documents = [
    "Enterprise segment generated a loss of 614545.62.",
    "Government segment generated a profit of 11388173.17.",
    "Paseo product generated the highest revenue of 33011143.95.",
    "USA generated the highest country revenue of 25029830.16."
]

ids = [
    "finance_001",
    "finance_002",
    "finance_003",
    "finance_004"
]

metadatas = [
    {"category": "segment", "name": "Enterprise"},
    {"category": "segment", "name": "Government"},
    {"category": "product", "name": "Paseo"},
    {"category": "country", "name": "USA"}
]

count = vector_store.add_documents(
    documents,
    ids,
    metadatas
)

print("Documents stored:", count)

results = vector_store.search(
    "Which business segment is making losses?",
    n_results=3
)

print("\nSEARCH RESULTS")

for document in results["documents"][0]:
    print("-", document)
