
from pydantic import BaseModel, Field


class AgentQuestionRequest(BaseModel):

    dataset_id: str = Field(
        ...,
        description="ID of the uploaded financial dataset"
    )

    question: str = Field(
        ...,
        min_length=3,
        description="Question for the financial AI assistant"
    )
