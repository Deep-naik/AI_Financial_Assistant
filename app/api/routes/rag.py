
from fastapi import APIRouter, HTTPException

from app.schemas.rag import (
    RAGQuestionRequest,
    RAGQuestionResponse
)

from app.services.rag_service import FinancialRAGService


router = APIRouter(
    prefix="/api/rag",
    tags=["RAG - Financial AI Assistant"]
)

rag_service = FinancialRAGService()


@router.post(
    "/ask",
    response_model=RAGQuestionResponse
)
def ask_financial_question(request: RAGQuestionRequest):

    try:
        result = rag_service.ask_question(
            question=request.question,
            n_results=request.n_results
        )

        return result

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"RAG processing failed: {str(error)}"
        )
