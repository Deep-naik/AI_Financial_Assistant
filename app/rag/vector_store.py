
import chromadb

from app.rag.embeddings import EmbeddingService


class FinancialVectorStore:

    def __init__(self):

        self.client = chromadb.PersistentClient(
            path="vector_store/chroma_db"
        )

        self.collection = self.client.get_or_create_collection(
            name="financial_knowledge",
            metadata={
                "description": "Financial business intelligence knowledge"
            }
        )

        self.embedding_service = EmbeddingService()

    def add_documents(
        self,
        documents: list[str],
        ids: list[str],
        metadatas: list[dict] | None = None
    ):

        embeddings = (
            self.embedding_service.generate_embeddings(
                documents
            )
        )

        self.collection.upsert(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas
        )

        return len(documents)

    def search(self, query, n_results=3, where=None):

        collection_count = self.collection.count()

        if collection_count == 0:
            return {
                "ids": [[]],
                "documents": [[]],
                "metadatas": [[]],
                "distances": [[]]
            }

        query_embedding = (
            self.embedding_service.generate_embedding(query)
        )

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=min(n_results, collection_count),
            where=where
        )

        return results
