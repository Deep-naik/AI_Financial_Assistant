
from app.rag.embeddings import EmbeddingService


embedding_service = EmbeddingService()

text = (
    "Enterprise segment generated a loss "
    "of 614545.62"
)

embedding = embedding_service.generate_embedding(text)

print("Embedding generated successfully!")
print("Embedding dimensions:", len(embedding))
print("First 5 values:", embedding[:5])
