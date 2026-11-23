
from io import BytesIO

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse

from app.database.connection import SessionLocal
from app.database.repository import get_dataset
from app.services.report_service import FinancialReportService

router = APIRouter(
    prefix="/api/reports",
    tags=["Financial Reports"]
)

report_service = FinancialReportService()


@router.get("/download")
def download_financial_report(
    dataset_id: str = Query(...)
):

    db = SessionLocal()

    try:

        dataset = get_dataset(db, dataset_id)

        if not dataset:
            raise HTTPException(
                status_code=404,
                detail="Dataset not found"
            )

        import pandas as pd

        df = pd.read_csv(
            dataset.processed_path,
            parse_dates=["date"]
        )

        pdf_content = report_service.generate_report(
            df,
            dataset_id
        )

        pdf_buffer = BytesIO(pdf_content)

        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={
                "Content-Disposition":
                    'attachment; filename="financial_intelligence_report.pdf"'
            }
        )

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
            detail=f"Report generation failed: {str(error)}"
        )

    finally:
        db.close()
