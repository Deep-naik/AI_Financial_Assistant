
import pandas as pd
import numpy as np

from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error
)

from statsmodels.tsa.holtwinters import ExponentialSmoothing


class FinancialForecastingService:

    def prepare_monthly_data(self, df: pd.DataFrame):

        df = df.copy()

        df["date"] = pd.to_datetime(df["date"])

        monthly = (
            df.groupby(
                df["date"].dt.to_period("M")
            )
            .agg(
                revenue=("sales", "sum"),
                profit=("profit", "sum")
            )
            .sort_index()
        )

        # Create a continuous monthly index.
        monthly.index = monthly.index.to_timestamp()

        full_index = pd.date_range(
            start=monthly.index.min(),
            end=monthly.index.max(),
            freq="MS"
        )

        # Missing months remain missing instead of becoming zero.
        monthly = monthly.reindex(full_index)
        monthly.index.name = "date"

        if monthly.isnull().any().any():
            raise ValueError(
                "Missing monthly observations detected. "
                "Forecasting requires investigation of missing months."
            )

        if len(monthly) < 8:
            raise ValueError(
                "At least 8 monthly observations are required."
            )

        return monthly

    def evaluate_forecast(self, actual, predicted):

        mae = mean_absolute_error(actual, predicted)

        rmse = np.sqrt(
            mean_squared_error(actual, predicted)
        )

        # MAPE is unreliable when actual values are zero
        # or very close to zero.
        actual = np.asarray(actual, dtype=float)
        predicted = np.asarray(predicted, dtype=float)

        non_zero_mask = np.abs(actual) > 1e-8

        if non_zero_mask.any():

            mape = np.mean(
                np.abs(
                    (actual[non_zero_mask] -
                     predicted[non_zero_mask]) /
                    actual[non_zero_mask]
                )
            ) * 100

        else:
            mape = None

        return {
            "mae": round(float(mae), 2),
            "rmse": round(float(rmse), 2),
            "mape_percentage": (
                round(float(mape), 2)
                if mape is not None
                else None
            )
        }

    
    
    def forecast_metric(
        self,
        monthly_data,
        metric,
        forecast_periods=3
    ):

        series = monthly_data[metric].astype(float)

        test_size = min(3, len(series) // 4)

        if len(series) - test_size < 5:
            raise ValueError(
                "Insufficient observations for model evaluation."
            )

        train = series.iloc[:-test_size]
        test = series.iloc[-test_size:]

        # --------------------------------
        # 1. Evaluate Naive Forecast
        # --------------------------------

        naive_predictions = np.repeat(
            train.iloc[-1],
            test_size
        )

        naive_evaluation = self.evaluate_forecast(
            test.values,
            naive_predictions
        )

        # --------------------------------
        # 2. Evaluate Holt Linear Trend
        # --------------------------------

        holt_model = ExponentialSmoothing(
            train,
            trend="add",
            seasonal=None,
            initialization_method="estimated"
        )

        holt_fitted = holt_model.fit(optimized=True)

        holt_predictions = holt_fitted.forecast(test_size)

        holt_evaluation = self.evaluate_forecast(
            test.values,
            holt_predictions.values
        )

        # --------------------------------
        # 3. Evaluate Seasonal Naive
        # --------------------------------

        seasonal_test_dates = (
            test.index - pd.DateOffset(years=1)
        )

        seasonal_predictions = train.reindex(
            seasonal_test_dates
        )

        seasonal_available = not seasonal_predictions.isnull().any()

        if seasonal_available:

            seasonal_evaluation = self.evaluate_forecast(
                test.values,
                seasonal_predictions.values
            )

        else:
            seasonal_evaluation = None

        # --------------------------------
        # 4. Compare Models Using MAE
        # --------------------------------

        model_evaluations = {
            "Naive Forecast": naive_evaluation,
            "Holt Linear Trend": holt_evaluation
        }

        if seasonal_available:

            model_evaluations[
                "Seasonal Naive"
            ] = seasonal_evaluation

        selected_model = min(
            model_evaluations,
            key=lambda model: model_evaluations[model]["mae"]
        )

        selected_evaluation = model_evaluations[
            selected_model
        ]

        # --------------------------------
        # 5. Generate Future Predictions
        # --------------------------------

        future_dates = pd.date_range(
            start=series.index[-1] + pd.offsets.MonthBegin(1),
            periods=forecast_periods,
            freq="MS"
        )

        if selected_model == "Naive Forecast":

            future_predictions = pd.Series(
                [series.iloc[-1]] * forecast_periods,
                index=future_dates
            )

        elif selected_model == "Holt Linear Trend":

            final_model = ExponentialSmoothing(
                series,
                trend="add",
                seasonal=None,
                initialization_method="estimated"
            )

            final_fitted = final_model.fit(optimized=True)

            future_predictions = final_fitted.forecast(
                forecast_periods
            )

        else:

            seasonal_future_dates = (
                future_dates - pd.DateOffset(years=1)
            )

            future_predictions = series.reindex(
                seasonal_future_dates
            )

            future_predictions.index = future_dates

        # Revenue cannot be negative, but profit can be.
        if metric == "revenue":

            future_predictions = future_predictions.clip(
                lower=0
            )

        # --------------------------------
        # 6. Format Forecast Results
        # --------------------------------

        forecast_records = []

        for date, value in future_predictions.items():

            forecast_records.append({
                "month": date.strftime("%Y-%m"),
                "predicted_value": round(float(value), 2)
            })

        return {
            "metric": metric,
            "selected_model": selected_model,
            "evaluation": selected_evaluation,
            "model_comparison": {
                "naive": naive_evaluation,
                "holt": holt_evaluation,
                "seasonal_naive": seasonal_evaluation
            },
            "forecast": forecast_records
        }


    def generate_forecasts(
        self,
        df: pd.DataFrame,
        forecast_periods=3
    ):

        monthly_data = self.prepare_monthly_data(df)

        if not 1 <= forecast_periods <= 12:
            raise ValueError(
                "Forecast period must be between 1 and 12 months."
            )

        revenue_forecast = self.forecast_metric(
            monthly_data,
            "revenue",
            forecast_periods
        )

        profit_forecast = self.forecast_metric(
            monthly_data,
            "profit",
            forecast_periods
        )

        return {
            "historical_months": len(monthly_data),
            "forecast_periods": forecast_periods,
            "model_selection_method": (
                            "Lowest MAE among Naive, Holt and Seasonal Naive "
                            "models on the same holdout test set"
                            ),
            "revenue_forecast": revenue_forecast,
            "profit_forecast": profit_forecast
        }
