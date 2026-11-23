
import pandas as pd
import numpy as np

class FinancialAnalyticsService:

    def calculate_kpis(self, df: pd.DataFrame):

        total_sales = float(df["sales"].sum())
        total_profit = float(df["profit"].sum())
        total_cogs = float(df["cogs"].sum())
        total_discounts = float(df["discounts"].sum())
        total_units = float(df["units_sold"].sum())

        profit_margin = (
            (total_profit / total_sales) * 100
            if total_sales != 0 else 0
        )

        average_sales = float(df["sales"].mean())
        average_profit = float(df["profit"].mean())

        loss_records = int((df["profit"] < 0).sum())
        profitable_records = int((df["profit"] > 0).sum())

        return {
            "total_records": len(df),

            "financial_kpis": {
                "total_sales": round(total_sales, 2),
                "total_profit": round(total_profit, 2),
                "total_cogs": round(total_cogs, 2),
                "total_discounts": round(total_discounts, 2),
                "total_units_sold": round(total_units, 2),
                "profit_margin_percentage": round(
                    profit_margin, 2
                )
            },

            "averages": {
                "average_sales_per_record": round(
                    average_sales, 2
                ),
                "average_profit_per_record": round(
                    average_profit, 2
                )
            },

            "profitability": {
                "profitable_records": profitable_records,
                "loss_making_records": loss_records,
                "zero_profit_records": int(
                    (df["profit"] == 0).sum()
                )
            }
        }

    def calculate_monthly_trends(self, df: pd.DataFrame):

        df = df.copy()

        df["date"] = pd.to_datetime(df["date"])

        monthly = (
            df.groupby(
                df["date"].dt.to_period("M")
            )
            .agg(
                revenue=("sales", "sum"),
                profit=("profit", "sum"),
                expenses=("cogs", "sum"),
                discounts=("discounts", "sum")
            )
            .reset_index()
        )

        monthly["date"] = (
            monthly["date"].astype(str)
        )

        # Calculate month-over-month growth
        monthly["revenue_growth"] = (
            monthly["revenue"].pct_change() * 100
        )

        monthly["profit_growth"] = (
            monthly["profit"].pct_change() * 100
        )

        # Replace undefined growth values
        monthly = monthly.fillna(0)

        records = []

        for _, row in monthly.iterrows():

            records.append({
                "month": row["date"],
                "revenue": round(float(row["revenue"]), 2),
                "profit": round(float(row["profit"]), 2),
                "expenses": round(float(row["expenses"]), 2),
                "discounts": round(float(row["discounts"]), 2),
                "revenue_growth_percentage": round(
                    float(row["revenue_growth"]), 2
                ),
                "profit_growth_percentage": round(
                    float(row["profit_growth"]), 2
                )
            })

        # Best and worst revenue months
        best_month = monthly.loc[
            monthly["revenue"].idxmax()
        ]

        worst_month = monthly.loc[
            monthly["revenue"].idxmin()
        ]

        return {
            "monthly_trends": records,

            "best_revenue_month": {
                "month": str(best_month["date"]),
                "revenue": round(
                    float(best_month["revenue"]), 2
                )
            },

            "worst_revenue_month": {
                "month": str(worst_month["date"]),
                "revenue": round(
                    float(worst_month["revenue"]), 2
                )
            }
        }


    def calculate_quarterly_trends(self, df: pd.DataFrame):

        df = df.copy()

        df["date"] = pd.to_datetime(df["date"])

        quarterly = (
            df.groupby(
                df["date"].dt.to_period("Q")
            )
            .agg(
                revenue=("sales", "sum"),
                profit=("profit", "sum"),
                expenses=("cogs", "sum")
            )
            .reset_index()
        )

        quarterly["revenue_growth"] = (
            quarterly["revenue"].pct_change() * 100
        )

        quarterly["profit_growth"] = (
            quarterly["profit"].pct_change() * 100
        )

        quarterly = quarterly.fillna(0)

        return [
            {
                "quarter": str(row["date"]),
                "revenue": round(float(row["revenue"]), 2),
                "profit": round(float(row["profit"]), 2),
                "expenses": round(float(row["expenses"]), 2),
                "revenue_growth_percentage": round(
                    float(row["revenue_growth"]), 2
                ),
                "profit_growth_percentage": round(
                    float(row["profit_growth"]), 2
                )
            }
            for _, row in quarterly.iterrows()
        ]

    def calculate_dimension_analysis(
        self,
        df: pd.DataFrame,
        dimension: str
    ):

        allowed_dimensions = [
            "product",
            "country",
            "segment"
        ]

        if dimension not in allowed_dimensions:
            raise ValueError("Invalid analysis dimension")

        if dimension not in df.columns:
            raise ValueError(
                f"Column {dimension} not found"
            )

        # Group data by selected dimension
        grouped = (
            df.groupby(dimension, dropna=False)
            .agg(
                revenue=("sales", "sum"),
                profit=("profit", "sum"),
                expenses=("cogs", "sum"),
                discounts=("discounts", "sum"),
                units_sold=("units_sold", "sum"),
                total_records=("profit", "size"),
                loss_records=(
                    "profit",
                    lambda values: (values < 0).sum()
                )
            )
            .reset_index()
        )

        # Calculate weighted profit margin
        grouped["profit_margin"] = (
            grouped["profit"] /
            grouped["revenue"].replace(0, float("nan"))
        ) * 100

        grouped["profit_margin"] = (
            grouped["profit_margin"].fillna(0)
        )

        # Sort by revenue
        grouped = grouped.sort_values(
            by="revenue",
            ascending=False
        )

        results = []

        for _, row in grouped.iterrows():

            results.append({

                "name": str(row[dimension]),

                "revenue": round(
                    float(row["revenue"]), 2
                ),

                "profit": round(
                    float(row["profit"]), 2
                ),

                "expenses": round(
                    float(row["expenses"]), 2
                ),

                "discounts": round(
                    float(row["discounts"]), 2
                ),

                "units_sold": round(
                    float(row["units_sold"]), 2
                ),

                "profit_margin_percentage": round(
                    float(row["profit_margin"]), 2
                ),

                "total_records": int(
                    row["total_records"]
                ),

                "loss_records": int(
                    row["loss_records"]
                )
            })

        return {

            "dimension": dimension,

            "total_categories": len(results),

            "results": results,

            "highest_revenue": (
                results[0] if results else None
            ),

            "lowest_revenue": (
                results[-1] if results else None
            )
        }

    def diagnose_profitability(
        self,
        df: pd.DataFrame,
        dimension: str
    ):

        allowed_dimensions = [
            "product",
            "country",
            "segment"
        ]

        if dimension not in allowed_dimensions:
            raise ValueError("Invalid analysis dimension")

        if dimension not in df.columns:
            raise ValueError(f"Column {dimension} not found")

        overall_sales = df["sales"].sum()
        overall_profit = df["profit"].sum()
        overall_margin = (
            overall_profit / overall_sales * 100
            if overall_sales else 0
        )

        grouped = (
            df.groupby(dimension, dropna=False)
            .agg(
                revenue=("sales", "sum"),
                profit=("profit", "sum"),
                expenses=("cogs", "sum"),
                discounts=("discounts", "sum"),
                total_records=("profit", "size"),
                loss_records=(
                    "profit",
                    lambda x: (x < 0).sum()
                )
            )
            .reset_index()
        )

        grouped["profit_margin"] = (
            grouped["profit"] /
            grouped["revenue"].replace(0, float("nan"))
        ) * 100

        grouped["profit_margin"] = (
            grouped["profit_margin"].fillna(0)
        )

        grouped["profit_contribution"] = (
            grouped["profit"] /
            overall_profit * 100
            if overall_profit != 0 else 0
        )

        grouped["revenue_contribution"] = (
            grouped["revenue"] /
            overall_sales * 100
            if overall_sales != 0 else 0
        )

        findings = []

        for _, row in grouped.iterrows():

            name = str(row[dimension])

            if row["profit"] < 0:

                findings.append({
                    "category": name,
                    "severity": "high",
                    "finding": "Loss-making category",
                    "details": (
                        f"{name} generated a loss of "
                        f"{abs(row['profit']):.2f}"
                    )
                })

            elif row["profit_margin"] < overall_margin:

                findings.append({
                    "category": name,
                    "severity": "medium",
                    "finding": "Below-average profit margin",
                    "details": (
                        f"{name} has a margin of "
                        f"{row['profit_margin']:.2f}%, "
                        f"below the overall margin of "
                        f"{overall_margin:.2f}%"
                    )
                })

            if row["loss_records"] > 0:

                findings.append({
                    "category": name,
                    "severity": "medium",
                    "finding": "Loss-making records detected",
                    "details": (
                        f"{int(row['loss_records'])} out of "
                        f"{int(row['total_records'])} records "
                        f"are loss-making"
                    )
                })

        grouped = grouped.sort_values(
            "profit",
            ascending=True
        )

        category_results = []

        for _, row in grouped.iterrows():

            category_results.append({

                "name": str(row[dimension]),

                "revenue": round(float(row["revenue"]), 2),

                "profit": round(float(row["profit"]), 2),

                "expenses": round(float(row["expenses"]), 2),

                "discounts": round(float(row["discounts"]), 2),

                "profit_margin_percentage": round(
                    float(row["profit_margin"]), 2
                ),

                "revenue_contribution_percentage": round(
                    float(row["revenue_contribution"]), 2
                ),

                "profit_contribution_percentage": round(
                    float(row["profit_contribution"]), 2
                ),

                "loss_records": int(row["loss_records"]),

                "total_records": int(row["total_records"])
            })

        return {

            "dimension": dimension,

            "overall_profit_margin": round(
                float(overall_margin), 2
            ),

            "total_revenue": round(
                float(overall_sales), 2
            ),

            "total_profit": round(
                float(overall_profit), 2
            ),

            "category_analysis": category_results,

            "diagnostic_findings": findings

        }

    def detect_financial_anomalies(self, df: pd.DataFrame):

        df = df.copy().reset_index(drop=True)

        financial_columns = [
            "sales",
            "profit",
            "discounts",
            "cogs"
        ]

        anomaly_records = []

        # 1. Identify negative-profit records
        for index, row in df[df["profit"] < 0].iterrows():

            anomaly_records.append({
                "record_index": int(index),
                "date": str(row["date"]),
                "product": str(row["product"]),
                "country": str(row["country"]),
                "segment": str(row["segment"]),
                "anomaly_type": "Negative Profit",
                "severity": "high",
                "value": round(float(row["profit"]), 2),
                "description": "Record generated a financial loss"
            })

        # 2. Detect statistical outliers using IQR
        statistical_counts = {}

        for column in financial_columns:

            q1 = df[column].quantile(0.25)
            q3 = df[column].quantile(0.75)

            iqr = q3 - q1

            lower_bound = q1 - (1.5 * iqr)
            upper_bound = q3 + (1.5 * iqr)

            outliers = df[
                (df[column] < lower_bound) |
                (df[column] > upper_bound)
            ]

            statistical_counts[column] = len(outliers)

            for index, row in outliers.iterrows():

                value = float(row[column])

                # Avoid creating duplicate anomaly
                # entries for negative profit.
                if column == "profit" and value < 0:
                    continue

                anomaly_records.append({

                    "record_index": int(index),

                    "date": str(row["date"]),

                    "product": str(row["product"]),

                    "country": str(row["country"]),

                    "segment": str(row["segment"]),

                    "anomaly_type": f"Unusual {column}",

                    "severity": "medium",

                    "value": round(value, 2),

                    "description": (
                        f"{column} is outside the "
                        "statistical IQR boundaries"
                    )
                })

        # 3. Calculate summary
        negative_profit_count = int(
            (df["profit"] < 0).sum()
        )

        return {

            "total_records": len(df),

            "total_anomalies": len(anomaly_records),

            "negative_profit_records": negative_profit_count,

            "statistical_outliers": statistical_counts,

            "anomaly_records": anomaly_records

        }
