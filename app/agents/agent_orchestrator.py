
from app.agents.analytics_agent import AnalyticsAgent
from app.agents.forecasting_agent import ForecastingAgent
from app.agents.rag_agent import RAGAgent


class AgentOrchestrator:

    def __init__(self):
        self.analytics_agent = AnalyticsAgent()
        self.forecasting_agent = ForecastingAgent()
        self.rag_agent = RAGAgent()

    def run(self, df, question: str):

        if not question or not question.strip():
            raise ValueError("Question cannot be empty.")

        question_lower = question.lower()

        # 1. Forecasting questions
        forecasting_keywords = [
            "forecast", "predict", "prediction",
            "future revenue", "future profit"
        ]

        if any(word in question_lower for word in forecasting_keywords):
            return self.forecasting_agent.run(df, question)

        # 2. Analytics questions
        analytics_keywords = [
            "kpi", "overall", "monthly", "quarterly",
            "anomaly", "anomalies", "outlier",
            "diagnose", "diagnostic", "breakdown",
            "performance", "trend", "total"
        ]

        if any(word in question_lower for word in analytics_keywords):
            return self.analytics_agent.run(df, question)

        # 3. Knowledge-based questions
        return self.rag_agent.run(question)
