
from app.services.rag_service import FinancialRAGService


class RAGAgent:

    def __init__(self):
        self.rag_service = FinancialRAGService()

    def run(self, question: str, n_results: int = 5):

        if not question or not question.strip():
            raise ValueError("Question cannot be empty.")

        result = self.rag_service.ask_question(
            question=question,
            n_results=n_results
        )

        return {
            "agent": "rag",
            "analysis_type": "knowledge_based_question_answering",
            "result": result
        }
