
from app.rag.vector_store import FinancialVectorStore

vector_store = FinancialVectorStore()

demo_ids = [
    "finance_001",
    "finance_002",
    "finance_003",
    "finance_004"
]

vector_store.collection.delete(ids=demo_ids)

print("Vector store cleanup completed.")
print(
    "Remaining documents:",
    vector_store.collection.count()
)
