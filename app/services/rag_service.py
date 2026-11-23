
from app.rag.retrieval import FinancialRetriever
from app.services.groq_service import GroqService


class FinancialRAGService:

    def __init__(self):
        self.retriever = FinancialRetriever()
        self.groq_service = GroqService()

    def detect_category(self, question: str):

        question = question.lower()

        if any(word in question for word in [
            "product", "products"
        ]):
            return "product"

        if any(word in question for word in [
            "country", "countries", "nation"
        ]):
            return "country"

        if any(word in question for word in [
            "segment", "segments"
        ]):
            return "segment"

        return None

    def ask_question(self, question: str, n_results: int = 5):

        if not question or not question.strip():
            raise ValueError("Question cannot be empty.")

        # 1. Detect the relevant financial category
        category = self.detect_category(question)

        # 2. Retrieve documents using category filter
        retrieved_results = self.retriever.retrieve(
            query=question,
            n_results=n_results,
            category=category
        )

        if not retrieved_results:
            return {
                "question": question,
                "answer": (
                    "I could not find relevant information "
                    "in the financial knowledge base."
                ),
                "sources": []
            }

        # 3. Build financial context
        context_parts = []

        for index, result in enumerate(retrieved_results, start=1):

            context_parts.append(
                f"""
                Source {index}
                Category: {result['metadata'].get('category')}
                Name: {result['metadata'].get('name')}
                Financial Information:
                {result['document']}
                """
            )

        context = "\n".join(context_parts)

        # 4. Instructions for Groq
        system_message = """
        You are an expert Financial Business Intelligence Assistant.

        Answer questions using only the supplied financial context.

        Rules:
        1. Never invent financial figures.
        2. Use the exact figures from the context.
        3. If information is insufficient, say so.
        4. Explain insights in simple language.
        5. Do not assume a currency symbol.
           Refer to amounts as dataset currency units.
        6. Provide practical recommendations when relevant.
        """

        user_message = f"""
        Financial Context:
        {context}

        User Question:
        {question}

        Answer using the financial context above.
        """

        # 5. Generate answer using Groq
        answer = self.groq_service.generate_response(
            user_message=user_message,
            system_message=system_message
        )

        # 6. Return answer and sources
        sources = [
            {
                "id": result["id"],
                "category": result["metadata"].get("category"),
                "name": result["metadata"].get("name"),
                "distance": result["distance"]
            }
            for result in retrieved_results
        ]

        return {
            "question": question,
            "category_filter": category,
            "answer": answer,
            "sources": sources
        }
