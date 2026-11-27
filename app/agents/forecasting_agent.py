
from app.services.forecasting_service import FinancialForecastingService


class ForecastingAgent:

    def __init__(self):
        self.forecasting_service = FinancialForecastingService()

    def run(self, df, question: str):

        if not question or not question.strip():
            raise ValueError("Question cannot be empty.")

        question_lower = question.lower()

        
        # Identify forecast period
        question_lower = question.lower().replace("-", " ")

        forecast_periods = 3

        if any(term in question_lower for term in [
            "twelve months", "12 months", "one year", "12 month"
        ]):
            forecast_periods = 12

        elif any(term in question_lower for term in [
            "six months", "6 months", "6 month"
        ]):
            forecast_periods = 6

        elif any(term in question_lower for term in [
            "three months", "3 months", "3 month"
        ]):
            forecast_periods = 3


        # Generate forecasts
        result = self.forecasting_service.generate_forecasts(
            df,
            forecast_periods=forecast_periods
        )

        # Build a simple English answer
        answer_lines = [
            f"Here is the profit forecast for the next {forecast_periods} months:"
        ]

        profit_forecast = result.get("profit_forecast", {})
        forecasts = profit_forecast.get("forecast", [])

        if forecasts:
            for item in forecasts:
                month = item.get("month", "Unknown month")
                value = item.get("predicted_value", 0)

                answer_lines.append(
                    f"- {month}: {value:,.2f}"
                )
        else:
            answer_lines.append(
                "Profit forecast values are not available."
            )

        selected_model = profit_forecast.get("selected_model")

        if selected_model:
            answer_lines.append(
                f"\nSelected forecasting model: {selected_model}"
            )

        evaluation = profit_forecast.get("evaluation", {})

        if evaluation:
            answer_lines.append(
                f"Model evaluation MAE: {evaluation.get('mae', 'N/A')}"
            )

        answer = "\n".join(answer_lines)

        return {
            "agent": "forecasting",
            "analysis_type": "financial_forecast",
            "forecast_periods": forecast_periods,
            "answer": answer,
            "result": result
        }
