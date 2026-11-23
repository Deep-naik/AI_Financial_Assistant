
import uuid
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, HTTPException

from app.services.data_service import DataProcessingService
from app.database.connection import SessionLocal


import pandas as pd

from fastapi import Path as APIPath
from app.database.repository import (
    save_dataset,
    delete_dataset,
    get_dataset,
    get_all_datasets
)

router = APIRouter(
    prefix="/api/data",
    tags=["Financial Data"]
)

service = DataProcessingService()

BASE_DIR = Path(__file__).resolve().parents[3]

UPLOAD_DIR = BASE_DIR / "data" / "uploads"
PROCESSED_DIR = BASE_DIR / "data" / "processed"

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

MAX_FILE_SIZE = 20 * 1024 * 1024

ALLOWED_EXTENSIONS = [".csv", ".xlsx"]


@router.post("/upload")
async def upload_dataset(file: UploadFile = File(...)):

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Filename is required"
        )

    extension = Path(file.filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Only CSV and XLSX files are supported"
        )

    dataset_id = str(uuid.uuid4())

    raw_path = UPLOAD_DIR / f"{dataset_id}{extension}"

    processed_path = (
        PROCESSED_DIR / f"{dataset_id}.csv"
    )

    try:

        content = await file.read(MAX_FILE_SIZE + 1)

        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail="File size exceeds 20 MB limit"
            )

        if not content:
            raise HTTPException(
                status_code=400,
                detail="Uploaded file is empty"
            )

        raw_path.write_bytes(content)

        # Load original dataset
        df = service.load_file(str(raw_path))

        # Clean and validate
        cleaned_df, quality_report = service.clean_data(df)

        # Save processed dataset
        cleaned_df.to_csv(
            processed_path,
            index=False
        )

        db = SessionLocal()

        try:

            dataset_data = {
                "dataset_id": dataset_id,
                "filename": file.filename,
                "file_path": str(raw_path),
                "processed_path": str(processed_path),
                "total_rows": len(cleaned_df),
                "total_columns": len(cleaned_df.columns),
                "status": "processed"
            }

            save_dataset(db, dataset_data)

        finally:
            db.close()

        return {
            "status": "success",
            "message": "Dataset uploaded and processed successfully",
            "dataset_id": dataset_id,
            "original_filename": file.filename,
            "rows": len(cleaned_df),
            "columns": len(cleaned_df.columns),
            "column_names": cleaned_df.columns.tolist(),
            "quality_report": quality_report
        }

    except HTTPException:
        raise

    except (ValueError, FileNotFoundError) as error:

        raise HTTPException(
            status_code=422,
            detail=str(error)
        )

    except Exception as error:

        raise HTTPException(
            status_code=400,
            detail=f"Unable to process dataset: {error}"
        )

    finally:

        await file.close()

        # Remove partially saved files if processing failed
        if not processed_path.exists():
            raw_path.unlink(missing_ok=True)

@router.get("/datasets")
def list_datasets():

    db = SessionLocal()

    try:

        datasets = get_all_datasets(db)

        return {
            "total_datasets": len(datasets),
            "datasets": [
                {
                    "dataset_id": item.dataset_id,
                    "filename": item.filename,
                    "total_rows": item.total_rows,
                    "total_columns": item.total_columns,
                    "upload_date": item.upload_date.isoformat()
                    if item.upload_date else None,
                    "status": item.status
                }
                for item in datasets
            ]
        }

    finally:
        db.close()


@router.get("/overview/{dataset_id}")
def dataset_overview(
    dataset_id: str = APIPath(...)
):

    db = SessionLocal()

    try:

        # Retrieve dataset metadata
        dataset = get_dataset(db, dataset_id)

        if not dataset:
            raise HTTPException(
                status_code=404,
                detail="Dataset not found"
            )

        # Load processed dataset
        df = pd.read_csv(
            dataset.processed_path,
            parse_dates=["date"]
        )

        # Column information
        column_info = {
            column: str(dtype)
            for column, dtype in df.dtypes.items()
        }

        # Missing values
        missing_values = {
            column: int(value)
            for column, value in df.isnull().sum().items()
        }

        # Numerical summary
        numeric_summary = {}

        numeric_df = df.select_dtypes(
            include="number"
        )

        for column in numeric_df.columns:

            numeric_summary[column] = {
                "mean": round(
                    float(numeric_df[column].mean()), 2
                ),
                "min": round(
                    float(numeric_df[column].min()), 2
                ),
                "max": round(
                    float(numeric_df[column].max()), 2
                ),
                "total": round(
                    float(numeric_df[column].sum()), 2
                )
            }

        # Categorical information
        categorical_summary = {}

        categorical_df = df.select_dtypes(
            include=["object", "string"]
        )

        for column in categorical_df.columns:

            categorical_summary[column] = {
                "unique_values": int(
                    categorical_df[column].nunique()
                ),
                "top_values": {
                    str(key): int(value)
                    for key, value in (
                        categorical_df[column]
                        .value_counts()
                        .head(5)
                        .items()
                    )
                }
            }

        # Financial KPIs
        financial_kpis = {}

        for column in [
            "sales",
            "profit",
            "gross_sales",
            "discounts",
            "cogs"
        ]:

            if column in df.columns:

                financial_kpis[column] = round(
                    float(df[column].sum()), 2
                )

        if "profit" in df.columns and "sales" in df.columns:

            total_sales = df["sales"].sum()

            profit_margin = (
                df["profit"].sum() / total_sales * 100
                if total_sales != 0 else 0
            )

            financial_kpis["profit_margin_percentage"] = round(
                float(profit_margin), 2
            )

        # Date range
        date_range = {}

        if "date" in df.columns:

            date_range = {
                "start_date": str(df["date"].min().date()),
                "end_date": str(df["date"].max().date())
            }

        return {

            "status": "success",

            "dataset": {
                "dataset_id": dataset.dataset_id,
                "filename": dataset.filename,
                "total_rows": len(df),
                "total_columns": len(df.columns),
                "upload_date": (
                    dataset.upload_date.isoformat()
                    if dataset.upload_date else None
                )
            },

            "columns": column_info,

            "missing_values": missing_values,

            "numerical_summary": numeric_summary,

            "categorical_summary": categorical_summary,

            "financial_kpis": financial_kpis,

            "date_range": date_range

        }

    finally:

        db.close()

@router.delete("/datasets/{dataset_id}")
def remove_dataset(dataset_id: str):

    db = SessionLocal()

    try:
        # Find dataset
        dataset = get_dataset(db, dataset_id)

        if not dataset:
            raise HTTPException(
                status_code=404,
                detail="Dataset not found"
            )

        filename = dataset.filename
        raw_path = Path(dataset.file_path).resolve()
        processed_path = Path(dataset.processed_path).resolve()

        # Ensure files belong to the application's dataset directories
        if (
            raw_path.parent != UPLOAD_DIR.resolve()
            or processed_path.parent != PROCESSED_DIR.resolve()
        ):
            raise HTTPException(
                status_code=400,
                detail="Invalid dataset file paths"
            )

        # Delete database record
        delete_dataset(db, dataset_id)

        # Delete original and processed files
        raw_path.unlink(missing_ok=True)
        processed_path.unlink(missing_ok=True)

        return {
            "status": "success",
            "message": "Dataset deleted successfully",
            "filename": filename
        }

    finally:
        db.close()