
import pandas as pd

from app.services.forecasting_service import FinancialForecastingService


# Load the existing cleaned dataset.
df = pd.read_csv(
    "data/processed/financial_sample_cleaned.csv"
)

# Prepare forecasting service.
forecast_service = FinancialForecastingService()

monthly_data = forecast_service.prepare_monthly_data(df)

print("\nMONTHLY DATA")
print(monthly_data)

print("\nSUMMARY")
print("Number of months:", len(monthly_data))
print("Start month:", monthly_data.index.min())
print("End month:", monthly_data.index.max())

print("\nMISSING VALUES")
print(monthly_data.isnull().sum())


print("\nGENERATING FINANCIAL FORECASTS")

forecast_results = forecast_service.generate_forecasts(
    df,
    forecast_periods=3
)

import json

print(json.dumps(
    forecast_results,
    indent=4
))

