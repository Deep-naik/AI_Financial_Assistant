
import pandas as pd

from app.rag.knowledge_builder import FinancialKnowledgeBuilder
from app.rag.vector_store import FinancialVectorStore


df = pd.read_csv(
    "data/processed/78667e6f-4ac9-4562-8e6f-c43b8211728f.csv"
)

# Build actual financial knowledge
builder = FinancialKnowledgeBuilder()

documents, ids, metadatas = builder.build_documents(df)

# Connect to vector store
vector_store = FinancialVectorStore()

# Remove previous demonstration documents
demo_ids = [
    "enterprise_loss",
    "government_profit",
    "paseo_revenue",
    "usa_revenue"
]

vector_store.collection.delete(ids=demo_ids)

# Store actual financial knowledge
count = vector_store.add_documents(
    documents=documents,
    ids=ids,
    metadatas=metadatas
)

print("\nKNOWLEDGE INDEXING RESULTS")
print("Documents indexed:", count)
print("Total documents in collection:", vector_store.collection.count())
