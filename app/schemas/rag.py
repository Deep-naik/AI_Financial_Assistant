
from pydantic import BaseModel, Field


class RAGQuestionRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=3,
        description="Financial question asked by the user"
    )

    n_results: int = Field(
        default=5,
        ge=1,
        le=17,
        description="Number of relevant documents to retrieve"
    )


class RAGSource(BaseModel):
    id: str
    category: str
    name: str
    distance: float


class RAGQuestionResponse(BaseModel):
    question: str
    category_filter: str | None
    answer: str
    sources: list[RAGSource]
