
import pandas as pd

from fastapi import APIRouter, HTTPException, Query

from app.database.connection import SessionLocal
from app.database.repository import get_dataset
from app.services.analytics_service import FinancialAnalyticsService

from typing import Literal

from app.services.forecasting_service import FinancialForecastingService
analytics_service = FinancialAnalyticsService()
forecasting_service = FinancialForecastingService()

router = APIRouter(
    prefix="/api/analytics",
    tags=["Financial Analytics"]
)

analytics_service = FinancialAnalyticsService()


@router.get("/kpis")
def get_financial_kpis(
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

        df = pd.read_csv(dataset.processed_path)

        result = analytics_service.calculate_kpis(df)

        return {
            "status": "success",
            "dataset_id": dataset_id,
            "analytics": result
        }

    finally:
        db.close()


@router.get("/trends")
def get_financial_trends(
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

        df = pd.read_csv(
            dataset.processed_path,
            parse_dates=["date"]
        )

        monthly = (
            analytics_service.calculate_monthly_trends(df)
        )

        quarterly = (
            analytics_service.calculate_quarterly_trends(df)
        )

        return {
            "status": "success",
            "dataset_id": dataset_id,

            "monthly_analysis": monthly,

            "quarterly_analysis": quarterly
        }

    finally:
        db.close()


@router.get("/breakdown")
def get_dimension_breakdown(
    dataset_id: str = Query(...),
    dimension: Literal[
        "product",
        "country",
        "segment"
    ] = Query(...)
):

    db = SessionLocal()

    try:

        dataset = get_dataset(db, dataset_id)

        if not dataset:
            raise HTTPException(
                status_code=404,
                detail="Dataset not found"
            )

        df = pd.read_csv(dataset.processed_path)

        result = analytics_service.calculate_dimension_analysis(
            df,
            dimension
        )

        return {
            "status": "success",
            "dataset_id": dataset_id,
            "analysis": result
        }

    finally:
        db.close()


@router.get("/diagnostics")
def get_financial_diagnostics(
    dataset_id: str = Query(...),
    dimension: Literal[
        "product",
        "country",
        "segment"
    ] = Query(...)
):

    db = SessionLocal()

    try:

        dataset = get_dataset(db, dataset_id)

        if not dataset:
            raise HTTPException(
                status_code=404,
                detail="Dataset not found"
            )

        df = pd.read_csv(dataset.processed_path)

        result = analytics_service.diagnose_profitability(
            df,
            dimension
        )

        return {
            "status": "success",
            "dataset_id": dataset_id,
            "diagnostics": result
        }

    finally:
        db.close()


@router.get("/anomalies")
def get_financial_anomalies(
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

        df = pd.read_csv(
            dataset.processed_path,
            parse_dates=["date"]
        )

        result = analytics_service.detect_financial_anomalies(
            df
        )

        return {
            "status": "success",
            "dataset_id": dataset_id,
            "anomaly_analysis": result
        }

    finally:
        db.close()


@router.get("/forecast")
def get_financial_forecast(
    dataset_id: str = Query(...),
    periods: int = Query(default=3, ge=1, le=12)
):

    db = SessionLocal()

    try:

        dataset = get_dataset(db, dataset_id)

        if not dataset:
            raise HTTPException(
                status_code=404,
                detail="Dataset not found"
            )

        df = pd.read_csv(
            dataset.processed_path,
            parse_dates=["date"]
        )

        result = forecasting_service.generate_forecasts(
            df,
            forecast_periods=periods
        )

        return {
            "status": "success",
            "dataset_id": dataset_id,
            "forecast_analysis": result
        }

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    finally:
        db.close()
