
import pandas as pd

from fastapi import APIRouter, HTTPException

from app.database.connection import SessionLocal
from app.database.repository import get_dataset

from app.schemas.agent import AgentQuestionRequest
from app.agents.agent_orchestrator import AgentOrchestrator


router = APIRouter(
    prefix="/api/agents",
    tags=["AI Multi-Agent System"]
)

orchestrator = AgentOrchestrator()


@router.post("/ask")
def ask_financial_question(request: AgentQuestionRequest):

    db = SessionLocal()

    try:

        # 1. Retrieve dataset
        dataset = get_dataset(db, request.dataset_id)

        if not dataset:
            raise HTTPException(
                status_code=404,
                detail="Dataset not found"
            )

        # 2. Load processed dataset
        df = pd.read_csv(
            dataset.processed_path,
            parse_dates=["date"]
        )

        # 3. Send question to the orchestrator
        result = orchestrator.run(
            df,
            request.question
        )

        # 4. Prepare agent response
        agent_result = result.get("result", {})

        # Include human-readable answer if provided by the agent
        if result.get("answer"):
            agent_result["answer"] = result["answer"]

        # Include forecast period information if available
        if result.get("forecast_periods"):
            agent_result["forecast_periods"] = result["forecast_periods"]

        # 5. Return agent response
        return {
            "status": "success",
            "dataset_id": request.dataset_id,
            "agent": result["agent"],
            "analysis_type": result["analysis_type"],
            "result": agent_result
        }

    except HTTPException:
        raise

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Agent processing failed: {str(error)}"
        )

    finally:
        db.close()
