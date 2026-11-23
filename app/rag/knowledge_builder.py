
from app.services.analytics_service import FinancialAnalyticsService


class FinancialKnowledgeBuilder:

    def __init__(self):
        self.analytics_service = FinancialAnalyticsService()

    def build_documents(self, df):

        documents = []
        metadatas = []
        ids = []

        # 1. Overall financial KPIs
        kpis = self.analytics_service.calculate_kpis(df)

        financial = kpis["financial_kpis"]
        profitability = kpis["profitability"]
        averages = kpis["averages"]

        documents.append(
            f"""
            Overall Financial Performance:
            Total Records: {kpis['total_records']}
            Total Revenue: {financial['total_sales']}
            Total Profit: {financial['total_profit']}
            Total COGS: {financial['total_cogs']}
            Total Discounts: {financial['total_discounts']}
            Total Units Sold: {financial['total_units_sold']}
            Profit Margin: {financial['profit_margin_percentage']}%
            Average Sales Per Record: {averages['average_sales_per_record']}
            Average Profit Per Record: {averages['average_profit_per_record']}
            Profitable Records: {profitability['profitable_records']}
            Loss Making Records: {profitability['loss_making_records']}
            Zero Profit Records: {profitability['zero_profit_records']}
            """
        )

        metadatas.append({
            "category": "overall",
            "name": "financial_kpis"
        })

        ids.append("overall_kpis")

        # 2. Product, country and segment performance
        for dimension in ["product", "country", "segment"]:

            analysis = self.analytics_service.calculate_dimension_analysis(
                df, dimension
            )

            for item in analysis["results"]:

                documents.append(
                    f"""
                    Dimension: {dimension}
                    Name: {item['name']}
                    Revenue: {item['revenue']}
                    Profit: {item['profit']}
                    Expenses: {item['expenses']}
                    Discounts: {item['discounts']}
                    Units Sold: {item['units_sold']}
                    Profit Margin: {item['profit_margin_percentage']}%
                    Total Records: {item['total_records']}
                    Loss Records: {item['loss_records']}
                    """
                )

                metadatas.append({
                    "category": dimension,
                    "name": item["name"]
                })

                ids.append(
                    f"{dimension}_{item['name'].lower().replace(' ', '_')}"
                )

        return documents, ids, metadatas
