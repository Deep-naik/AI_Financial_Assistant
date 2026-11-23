
import pandas as pd
import numpy as np

from app.services.forecasting_service import (
    FinancialForecastingService
)

from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error
)


df = pd.read_csv(
    "data/processed/financial_sample_cleaned.csv"
)

service = FinancialForecastingService()

monthly_data = service.prepare_monthly_data(df)

test_size = 3

for metric in ["revenue", "profit"]:

    train = monthly_data[metric].iloc[:-test_size]
    test = monthly_data[metric].iloc[-test_size:]

    # Naive forecast: repeat the last observed value.
    naive_predictions = np.repeat(
        train.iloc[-1],
        test_size
    )

    # Holt trend forecast.
    from statsmodels.tsa.holtwinters import ExponentialSmoothing

    model = ExponentialSmoothing(
        train,
        trend="add",
        seasonal=None,
        initialization_method="estimated"
    )

    fitted = model.fit(optimized=True)

    holt_predictions = fitted.forecast(test_size)

    print(f"\nMETRIC: {metric.upper()}")

    for model_name, predictions in [
        ("Naive", naive_predictions),
        ("Holt", holt_predictions.values)
    ]:

        mae = mean_absolute_error(
            test.values,
            predictions
        )

        rmse = np.sqrt(
            mean_squared_error(
                test.values,
                predictions
            )
        )

        print(f"\n{model_name} Model")
        print("MAE:", round(mae, 2))
        print("RMSE:", round(rmse, 2))
