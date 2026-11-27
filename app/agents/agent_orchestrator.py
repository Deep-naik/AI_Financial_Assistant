
import json

from app.agents.analytics_agent import AnalyticsAgent
from app.agents.forecasting_agent import ForecastingAgent
from app.agents.rag_agent import RAGAgent

from app.services.analytics_service import FinancialAnalyticsService
from app.services.groq_service import GroqService


class AgentOrchestrator:

    def __init__(self):
        self.analytics_agent = AnalyticsAgent()
        self.forecasting_agent = ForecastingAgent()
        self.rag_agent = RAGAgent()

        self.analytics_service = FinancialAnalyticsService()
        self.groq_service = GroqService()

    def run(self, df, question: str):

        if not question or not question.strip():
            raise ValueError("Question cannot be empty.")

        question_lower = question.lower()

        # 1. Comprehensive financial health assessment
        comprehensive_keywords = [
            "financial health",
            "comprehensive assessment",
            "complete financial assessment",
            "business assessment",
            "major financial risks",
            "actionable recommendations",
            "complete financial analysis"
        ]

        if any(word in question_lower for word in comprehensive_keywords):
            return self.run_financial_health_assessment(
                df, question
            )

        # 2. Forecasting questions
        forecasting_keywords = [
            "forecast", "forecasts", "forecasting",
            "predict", "prediction", "predictions",
            "expected revenue", "expected profit",
            "expected sales", "expected earnings",
            "next month", "next months",
            "next quarter", "next year",
            "coming months", "coming quarter",
            "future revenue", "future profit",
            "future sales", "future earnings",
            "how much will", "what will be",
            "estimate future", "projected revenue",
            "projected profit"
        ]

        if any(word in question_lower for word in forecasting_keywords):
            return self.forecasting_agent.run(df, question)

        # 3. Analytics questions
        analytics_keywords = [
            "kpi", "overall", "monthly", "quarterly",
            "anomaly", "anomalies", "outlier",
            "diagnose", "diagnostic", "breakdown",
            "performance", "trend", "total",
            "revenue", "profit", "sales",
            "discount", "cogs", "margin"
        ]

        if any(word in question_lower for word in analytics_keywords):
            return self.analytics_agent.run(df, question)

        # 4. Knowledge-based questions
        return self.rag_agent.run(question)

    def run_financial_health_assessment(self, df, question: str):

        # A. Retrieve overall financial KPIs
        kpi_response = self.analytics_agent.run(
            df,
            "Give me the overall financial summary"
        )

        kpis = kpi_response["result"]

        # B. Calculate segment performance
        segment_analysis = self.analytics_service.calculate_dimension_analysis(
            df,
            "segment"
        )

        # C. Diagnose segment profitability
        segment_diagnostics = self.analytics_service.diagnose_profitability(
            df,
            "segment"
        )

        categories = segment_diagnostics.get(
            "category_analysis", []
        )

        best_segment = None
        worst_segment = None

        if categories:
            best_segment = max(
                categories,
                key=lambda item: item["profit"]
            )

            worst_segment = min(
                categories,
                key=lambda item: item["profit"]
            )

        # D. Retrieve relevant financial knowledge
        try:
            rag_response = self.rag_agent.run(
                question,
                n_results=5
            )

            rag_context = rag_response.get("result", {})

        except Exception as error:
            rag_context = {
                "note": (
                    "RAG knowledge retrieval was unavailable: "
                    + str(error)
                )
            }

        # E. Prepare consolidated evidence
        assessment_data = {
            "financial_kpis": kpis,
            "segment_analysis": segment_analysis,
            "segment_diagnostics": segment_diagnostics,
            "best_profit_segment": best_segment,
            "worst_profit_segment": worst_segment,
            "retrieved_knowledge": rag_context
        }

        # F. Generate final assessment using Groq
        user_message = f"""
USER QUESTION:
{question}

AVAILABLE FINANCIAL DATA:
{json.dumps(assessment_data, indent=2, default=str)}

Prepare a comprehensive financial health assessment.

Include the following sections:

1. Overall Financial Performance
   - Total revenue
   - Total profit
   - Profit margin
   - Other relevant KPIs

2. Segment Performance
   - Best-performing segment
   - Worst-performing segment
   - Explain their financial performance

3. Major Financial Risks
   - Identify loss-making segments
   - Explain below-average profit margins
   - Discuss loss-making transaction records
   - Mention other risks supported by the data

4. Actionable Recommendations
   - Suggest practical improvements
   - Connect recommendations to the identified financial risks

IMPORTANT:
- Use simple, professional English.
- Use the supplied financial figures accurately.
- Do not invent financial values.
- Do not claim that an unsupported cause is proven.
- Clearly distinguish actual findings from recommendations.
- Use retrieved knowledge only when relevant.
- If information is unavailable, say so.
- Avoid generic recommendations that are not connected
  to the financial findings.
"""

        system_message = """
You are an expert financial business intelligence analyst.

Your task is to prepare evidence-based financial assessments
using the supplied analytics results and retrieved knowledge.

Follow these rules:

1. Use the supplied analytics as the source of truth for
   numerical financial results.
2. Never invent or modify financial figures.
3. Explain findings in simple, understandable English.
4. Distinguish facts, interpretations and recommendations.
5. Do not present possible causes as confirmed facts.
6. Provide practical and relevant business recommendations.
7. Structure the response with clear headings and bullet points.
"""

        answer = self.groq_service.generate_response(
            user_message=user_message,
            system_message=system_message
        )

        # G. Return consolidated multi-agent response
        return {
            "agent": "multi_agent",
            "analysis_type": "financial_health_assessment",
            "answer": answer,
            "result": {
                "financial_kpis": kpis,
                "segment_analysis": segment_analysis,
                "segment_diagnostics": segment_diagnostics,
                "best_profit_segment": best_segment,
                "worst_profit_segment": worst_segment,
                "rag_context": rag_context
            }
        }
