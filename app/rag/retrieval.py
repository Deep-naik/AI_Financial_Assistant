
from app.rag.vector_store import FinancialVectorStore


class FinancialRetriever:

    def __init__(self):
        self.vector_store = FinancialVectorStore()

    def retrieve(
        self,
        query: str,
        n_results: int = 5,
        category: str = None
    ):

        if not query or not query.strip():
            raise ValueError("Query cannot be empty.")

        if n_results < 1:
            raise ValueError("n_results must be at least 1.")

        valid_categories = [
            "overall",
            "product",
            "country",
            "segment"
        ]

        if category and category not in valid_categories:
            raise ValueError(
                f"Invalid category. Choose from {valid_categories}"
            )

        # Search only within the requested category when supplied
        where_filter = (
            {"category": category}
            if category
            else None
        )

        results = self.vector_store.search(
            query=query,
            n_results=n_results,
            where=where_filter
        )

        retrieved_documents = []

        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]
        ids = results.get("ids", [[]])[0]

        for document, metadata, distance, doc_id in zip(
            documents, metadatas, distances, ids
        ):

            retrieved_documents.append({
                "id": doc_id,
                "document": document,
                "metadata": metadata,
                "distance": distance
            })

        return retrieved_documents
