
from app.services.analytics_service import FinancialAnalyticsService


class AnalyticsAgent:

    def __init__(self):
        self.analytics_service = FinancialAnalyticsService()

    def run(self, df, question: str):

        if not question or not question.strip():
            raise ValueError("Question cannot be empty.")

        question_lower = question.lower()

        # 1. Overall financial KPIs
        if any(word in question_lower for word in [
            "overall", "total", "kpi", "performance",
            "financial summary"
        ]):

            kpis = self.analytics_service.calculate_kpis(df)

            financial = kpis["financial_kpis"]
            profitability = kpis["profitability"]
            averages = kpis["averages"]

            answer = (
                f"Here is the overall financial performance summary:\n\n"
                f"- Total Revenue: {financial['total_sales']:,.2f}\n"
                f"- Total Profit: {financial['total_profit']:,.2f}\n"
                f"- Total COGS: {financial['total_cogs']:,.2f}\n"
                f"- Total Discounts: {financial['total_discounts']:,.2f}\n"
                f"- Total Units Sold: {financial['total_units_sold']:,.0f}\n"
                f"- Profit Margin: {financial['profit_margin_percentage']}%\n"
                f"- Average Sales Per Record: "
                f"{averages['average_sales_per_record']:,.2f}\n"
                f"- Profitable Records: {profitability['profitable_records']}\n"
                f"- Loss-Making Records: {profitability['loss_making_records']}\n"
            )

            kpis["answer"] = answer

            return {
                "agent": "analytics",
                "analysis_type": "kpis",
                "result": kpis
            }

        # 2. Monthly trends
        if any(word in question_lower for word in [
            "monthly", "month", "monthly trend"
        ]):
            return {
                "agent": "analytics",
                "analysis_type": "monthly_trends",
                "result": self.analytics_service.calculate_monthly_trends(df)
            }

        # 3. Quarterly trends
        if any(word in question_lower for word in [
            "quarterly", "quarter"
        ]):
            return {
                "agent": "analytics",
                "analysis_type": "quarterly_trends",
                "result": self.analytics_service.calculate_quarterly_trends(df)
            }

        # 4. Financial anomalies
        if any(word in question_lower for word in [
            "anomaly", "anomalies", "outlier", "unusual"
        ]):
            return {
                "agent": "analytics",
                "analysis_type": "anomalies",
                "result": self.analytics_service.detect_financial_anomalies(df)
            }

        # 5. Identify dimension
        dimension = None

        if "product" in question_lower:
            dimension = "product"

        elif "country" in question_lower or "countries" in question_lower:
            dimension = "country"

        elif "segment" in question_lower:
            dimension = "segment"

        if dimension:

            # 6. Profitability diagnostics
            if any(word in question_lower for word in [
                "diagnose", "diagnostic", "why", "reason",
                "loss", "losses", "problem"
            ]):
                return {
                    "agent": "analytics",
                    "analysis_type": "profitability_diagnostics",
                    "result": self.analytics_service.diagnose_profitability(
                        df, dimension
                    )
                }

            
            # 7. Dimension analysis
            analysis = self.analytics_service.calculate_dimension_analysis(
                df, dimension
            )

            results = analysis.get("results", [])

            answer = "No dimension analysis results are available."

            if results:

                # Identify the metric requested
                if "profit margin" in question_lower or "margin" in question_lower:
                    metric = "profit_margin_percentage"
                    metric_name = "profit margin"
                    suffix = "%"
                elif "profit" in question_lower:
                    metric = "profit"
                    metric_name = "profit"
                    suffix = ""
                elif "revenue" in question_lower or "sales" in question_lower:
                    metric = "revenue"
                    metric_name = "revenue"
                    suffix = ""
                elif "units" in question_lower:
                    metric = "units_sold"
                    metric_name = "units sold"
                    suffix = ""
                elif "discount" in question_lower:
                    metric = "discounts"
                    metric_name = "discounts"
                    suffix = ""
                elif "expense" in question_lower or "cogs" in question_lower:
                    metric = "expenses"
                    metric_name = "expenses"
                    suffix = ""
                else:
                    metric = "revenue"
                    metric_name = "revenue"
                    suffix = ""

                # Identify highest or lowest category
                lowest_requested = any(word in question_lower for word in [
                    "lowest", "least", "minimum", "worst"
                ])

                if lowest_requested:
                    best_category = min(
                        results,
                        key=lambda item: item[metric]
                    )
                    comparison = "lowest"
                else:
                    best_category = max(
                        results,
                        key=lambda item: item[metric]
                    )
                    comparison = "highest"

                category_name = best_category["name"]
                metric_value = best_category[metric]

                formatted_value = f"{metric_value:,.2f}{suffix}"

                answer = (
                    f"{category_name} generated the {comparison} "
                    f"{metric_name} among all {dimension}s, "
                    f"with {formatted_value}."
                )

                # Add additional context
                answer += (
                    f"\n\nIts total revenue was "
                    f"{best_category['revenue']:,.2f} "
                    f"and its total profit was "
                    f"{best_category['profit']:,.2f}."
                )

                answer += (
                    f"\nIts profit margin was "
                    f"{best_category['profit_margin_percentage']}%."
                )

            analysis["answer"] = answer

            return {
                "agent": "analytics",
                "analysis_type": "dimension_analysis",
                "result": analysis
            }


        raise ValueError(
            "Unable to identify the requested analytics operation."
        )
