
from app.services.forecasting_service import FinancialForecastingService


class ForecastingAgent:

    def __init__(self):
        self.forecasting_service = FinancialForecastingService()

    def run(self, df, question: str):

        if not question or not question.strip():
            raise ValueError("Question cannot be empty.")

        question_lower = question.lower()

        # Identify forecast period
        forecast_periods = 3

        if "six months" in question_lower or "6 months" in question_lower:
            forecast_periods = 6

        elif "twelve months" in question_lower or "12 months" in question_lower:
            forecast_periods = 12

        elif "one year" in question_lower:
            forecast_periods = 12

        # Generate forecasts
        result = self.forecasting_service.generate_forecasts(
            df,
            forecast_periods=forecast_periods
        )

        return {
            "agent": "forecasting",
            "analysis_type": "financial_forecast",
            "forecast_periods": forecast_periods,
            "result": result
        }
