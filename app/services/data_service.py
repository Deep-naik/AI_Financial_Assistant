
import pandas as pd
from pathlib import Path


class DataProcessingService:

    REQUIRED_COLUMNS = ["Date", "Sales", "Profit"]

    def load_file(self, file_path: str) -> pd.DataFrame:

        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError("Dataset file not found")

        extension = path.suffix.lower()

        if extension == ".csv":
            df = pd.read_csv(path)

        elif extension == ".xlsx":
            df = pd.read_excel(path)

        else:
            raise ValueError(
                "Only CSV and Excel files are supported"
            )

        return df

    def standardize_columns(self, df: pd.DataFrame):

        df = df.copy()

        df.columns = (
            df.columns
            .str.strip()
            .str.replace(r"\s+", "_", regex=True)
            .str.lower()
        )

        return df

    def validate_columns(self, df: pd.DataFrame):

        missing_columns = [
            column
            for column in self.REQUIRED_COLUMNS
            if column.lower() not in df.columns
        ]

        if missing_columns:
            raise ValueError(
                f"Missing required columns: {missing_columns}"
            )

        return True

    def clean_data(self, df: pd.DataFrame):

        df = self.standardize_columns(df)

        self.validate_columns(df)

        initial_rows = len(df)

        # Convert date column
        df["date"] = pd.to_datetime(
            df["date"],
            errors="coerce"
        )

        # Convert financial columns to numeric
        numeric_columns = [
            "sales",
            "profit",
            "gross_sales",
            "discounts",
            "cogs",
            "units_sold"
        ]

        for column in numeric_columns:

            if column in df.columns:

                df[column] = pd.to_numeric(
                    df[column],
                    errors="coerce"
                )

        # Handle missing Discount Band
        if "discount_band" in df.columns:

            df["discount_band"] = (
                df["discount_band"].fillna("Unknown")
            )

            if "discounts" in df.columns:

                zero_discount = (
                    df["discounts"].eq(0)
                    & df["discount_band"].eq("Unknown")
                )

                df.loc[
                    zero_discount,
                    "discount_band"
                ] = "No Discount"

        duplicate_count = int(df.duplicated().sum())

        missing_values = (
            df.isnull().sum()
            .to_dict()
        )

        quality_report = {
            "initial_rows": initial_rows,
            "final_rows": len(df),
            "columns": len(df.columns),
            "duplicate_rows": duplicate_count,
            "missing_values": {
                key: int(value)
                for key, value in missing_values.items()
            }
        }

        return df, quality_report
