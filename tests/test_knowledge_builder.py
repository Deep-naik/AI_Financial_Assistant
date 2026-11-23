
import pandas as pd

from app.rag.knowledge_builder import FinancialKnowledgeBuilder


df = pd.read_csv(
    "data/processed/financial_sample_cleaned.csv"
)

builder = FinancialKnowledgeBuilder()

documents, ids, metadatas = builder.build_documents(df)

print("\nKNOWLEDGE BUILDING RESULTS")
print("Total documents:", len(documents))

print("\nDOCUMENT CATEGORIES")

for metadata in metadatas:
    print(metadata)

print("\nENTERPRISE FINANCIAL DOCUMENT")

for document, metadata in zip(documents, metadatas):

    if metadata["name"] == "Enterprise":
        print(document)
        break
