
from io import BytesIO
from datetime import datetime

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    Image,
    KeepTogether
)

from app.services.analytics_service import FinancialAnalyticsService
from app.services.forecasting_service import FinancialForecastingService


class FinancialReportService:

    def __init__(self):
        self.analytics_service = FinancialAnalyticsService()
        self.forecasting_service = FinancialForecastingService()

    # --------------------------------
    # HELPER: ADD CHART TO PDF
    # --------------------------------

    def add_chart(self, story, figure, width=6.7 * inch, height=2.9 * inch):

        chart_buffer = BytesIO()

        figure.savefig(
            chart_buffer,
            format="png",
            dpi=160,
            bbox_inches="tight"
        )

        chart_buffer.seek(0)

        chart_image = Image(
            chart_buffer,
            width=width,
            height=height,
            kind="proportional"
        )

        story.append(chart_image)
        story.append(Spacer(1, 5))

        plt.close(figure)
    # --------------------------------
    # HELPER: CREATE TABLE
    # --------------------------------

    def create_table(self, headers, rows):

        table_data = [headers] + rows

        table = Table(
            table_data,
            repeatRows=1,
            hAlign="LEFT"
        )

        table.setStyle(
            TableStyle([
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor("#17365D")
                ),
                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    colors.white
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.4,
                    colors.grey
                ),
                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold"
                ),
                (
                    "FONTSIZE",
                    (0, 0),
                    (-1, -1),
                    7
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE"
                ),
                (
                    "ROWBACKGROUNDS",
                    (0, 1),
                    (-1, -1),
                    [
                        colors.white,
                        colors.HexColor("#EAF0F8")
                    ]
                ),
                (
                    "TOPPADDING", 
                    (0, 0), 
                    (-1, -1),
                     3
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0), 
                    (-1, -1), 
                    3
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    5
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    5
                )
            ])
        )

        return table

    # --------------------------------
    # GENERATE FINANCIAL REPORT
    # --------------------------------

    def generate_report(self, df, dataset_id):

        buffer = BytesIO()

        document = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=30,
            leftMargin=30,
            topMargin=30,
            bottomMargin=30
        )

        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            "ReportTitle",
            parent=styles["Title"],
            alignment=TA_CENTER,
            textColor=colors.HexColor("#17365D"),
            fontSize=20,
            spaceAfter=12
        )

        heading_style = ParagraphStyle(
            "SectionHeading",
            parent=styles["Heading2"],
            textColor=colors.HexColor("#17365D"),
            spaceBefore=8,
            spaceAfter=4
        )

        story = []

        # --------------------------------
        # REPORT TITLE
        # --------------------------------

        story.append(
            Paragraph(
                "Financial Intelligence Report",
                title_style
            )
        )

        story.append(
            Paragraph(
                "AI-Powered Business Intelligence and Decision Support System",
                styles["Normal"]
            )
        )

        story.append(Spacer(1, 5))

        story.append(
            Paragraph(
                f"Dataset ID: {dataset_id}",
                styles["Normal"]
            )
        )

        story.append(
            Paragraph(
                f"Report Generated: {datetime.now().strftime('%d-%m-%Y %H:%M')}",
                styles["Normal"]
            )
        )

        story.append(Spacer(1, 15))

        # --------------------------------
        # 1. OVERALL FINANCIAL KPIs
        # --------------------------------

        story.append(
            Paragraph(
                "1. Overall Financial Performance",
                heading_style
            )
        )

        kpis = self.analytics_service.calculate_kpis(df)

        financial = kpis["financial_kpis"]
        averages = kpis["averages"]
        profitability = kpis["profitability"]

        kpi_rows = [
            ["Total Records", str(kpis["total_records"])],
            ["Total Revenue", f'{financial["total_sales"]:,.2f}'],
            ["Total Profit", f'{financial["total_profit"]:,.2f}'],
            ["Total COGS", f'{financial["total_cogs"]:,.2f}'],
            ["Total Discounts", f'{financial["total_discounts"]:,.2f}'],
            ["Units Sold", f'{financial["total_units_sold"]:,.0f}'],
            ["Profit Margin", f'{financial["profit_margin_percentage"]:.2f}%'],
            ["Average Revenue per Record", f'{averages["average_sales_per_record"]:,.2f}'],
            ["Average Profit per Record", f'{averages["average_profit_per_record"]:,.2f}'],
            ["Profitable Records", str(profitability["profitable_records"])],
            ["Loss-Making Records", str(profitability["loss_making_records"])],
            ["Zero-Profit Records", str(profitability["zero_profit_records"])]
        ]

        story.append(
            self.create_table(
                ["Financial Indicator", "Value"],
                kpi_rows
            )
        )

        story.append(Spacer(1, 5))

        # --------------------------------
        # CHART 1: OVERALL PERFORMANCE
        # --------------------------------

        fig, ax = plt.subplots(figsize=(8, 4))

        categories = ["Revenue", "COGS", "Profit"]

        values = [
            financial["total_sales"],
            financial["total_cogs"],
            financial["total_profit"]
        ]

        bars = ax.bar(categories, values)

        ax.set_title("Overall Financial Performance")
        ax.set_ylabel("Amount (Dataset Currency Units)")
        ax.grid(axis="y", alpha=0.3)
     
        for bar, value in zip(bars, values):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height(),
                f"{value / 1_000_000:.1f}M",
                ha="center",
                va="bottom"
            )

        fig.tight_layout()
        self.add_chart(story, fig)

        # --------------------------------
        # 2. PRODUCT, COUNTRY AND SEGMENT
        # --------------------------------

        dimensions = [
            ("Product", "product"),
            ("Country", "country"),
            ("Segment", "segment")
        ]

        for title, dimension in dimensions:

            story.append(
                Paragraph(
                    f"{title} Performance Analysis",
                    heading_style
                )
            )

            analysis = self.analytics_service.calculate_dimension_analysis(
                df,
                dimension
            )

            rows = []

            for item in analysis["results"]:

                rows.append([
                    str(item["name"]),
                    f'{item["revenue"]:,.2f}',
                    f'{item["profit"]:,.2f}',
                    f'{item["profit_margin_percentage"]:.2f}%',
                    str(item["loss_records"])
                ])

            story.append(
                self.create_table(
                    [
                        title,
                        "Revenue",
                        "Profit",
                        "Margin",
                        "Loss Records"
                    ],
                    rows
                )
            )

            story.append(Spacer(1, 5))

            # --------------------------------
            # CHART 2: PRODUCT PERFORMANCE
            # --------------------------------

            if dimension == "product":

                names = [
                    item["name"]
                    for item in analysis["results"]
                ]

                revenues = [
                    item["revenue"]
                    for item in analysis["results"]
                ]

                profits = [
                    item["profit"]
                    for item in analysis["results"]
                ]

                fig, ax = plt.subplots(figsize=(8, 4))

                x = range(len(names))
                width = 0.35

                ax.bar(
                    [i - width / 2 for i in x],
                    revenues,
                    width,
                    label="Revenue"
                )

                ax.bar(
                    [i + width / 2 for i in x],
                    profits,
                    width,
                    label="Profit"
                )

                ax.set_xticks(list(x))
                ax.set_xticklabels(names)

                ax.set_title("Product-wise Revenue and Profit")
                ax.set_ylabel("Amount (Dataset Currency Units)")

                ax.legend()
                ax.grid(axis="y", alpha=0.3)

                fig.tight_layout()
                self.add_chart(story, fig)

            # --------------------------------
            # CHART 3: COUNTRY REVENUE
            # --------------------------------

            elif dimension == "country":

                countries = [
                    item["name"]
                    for item in analysis["results"]
                ]

                revenues = [
                    item["revenue"]
                    for item in analysis["results"]
                ]

                fig, ax = plt.subplots(figsize=(8, 4))

                bars = ax.barh(countries, revenues)

                ax.set_title("Country-wise Revenue")
                ax.set_xlabel("Revenue (Dataset Currency Units)")
                ax.invert_yaxis()
                ax.grid(axis="x", alpha=0.3)

                for bar, value in zip(bars, revenues):

                    ax.text(
                        bar.get_width(),
                        bar.get_y() + bar.get_height() / 2,
                        f" {value / 1_000_000:.1f}M",
                        va="center"
                    )

                fig.tight_layout()
                self.add_chart(story, fig)

            # --------------------------------
            # CHART 4: SEGMENT PROFIT MARGIN
            # --------------------------------

            elif dimension == "segment":

                segments = [
                    item["name"]
                    for item in analysis["results"]
                ]

                margins = [
                    item["profit_margin_percentage"]
                    for item in analysis["results"]
                ]

                fig, ax = plt.subplots(figsize=(8, 4))

                bars = ax.barh(segments, margins)

                ax.axvline(0, linewidth=1, color="black")
                ax.set_title("Segment-wise Profit Margin")
                ax.set_xlabel("Profit Margin (%)")
                ax.invert_yaxis()
                ax.grid(axis="x", alpha=0.3)

                # Add space around the bars for labels
                ax.margins(x=0.20)

                for bar, value in zip(bars, margins):

                    ax.annotate(
                        f"{value:.2f}%",
                        xy=(
                            value,
                            bar.get_y() + bar.get_height() / 2
                        ),
                        xytext=(
                            5 if value >= 0 else -5,
                            0
                        ),
                        textcoords="offset points",
                        va="center",
                        ha="left" if value >= 0 else "right"
                    )

                fig.tight_layout()
                self.add_chart(story, fig)

        # --------------------------------
        # 3. MONTHLY FINANCIAL TRENDS
        # --------------------------------

        story.append(
            Paragraph(
                "Monthly Financial Trends",
                heading_style
            )
        )

        monthly = self.analytics_service.calculate_monthly_trends(df)

        monthly_data = monthly["monthly_trends"]

        monthly_rows = []

        for item in monthly_data:

            monthly_rows.append([
                item["month"],
                f'{item["revenue"]:,.2f}',
                f'{item["profit"]:,.2f}'
            ])

        story.append(
            self.create_table(
                ["Month", "Revenue", "Profit"],
                monthly_rows
            )
        )

        story.append(Spacer(1, 5))

        # --------------------------------
        # CHART 5: MONTHLY REVENUE AND PROFIT
        # --------------------------------

        months = [
            item["month"]
            for item in monthly_data
        ]

        monthly_revenue = [
            item["revenue"]
            for item in monthly_data
        ]

        monthly_profit = [
            item["profit"]
            for item in monthly_data
        ]

        fig, ax = plt.subplots(figsize=(9, 4))

        ax.plot(
            months,
            monthly_revenue,
            marker="o",
            label="Revenue"
        )

        ax.plot(
            months,
            monthly_profit,
            marker="s",
            label="Profit"
        )

        ax.set_title("Monthly Revenue and Profit Trends")
        ax.set_xlabel("Month")
        ax.set_ylabel("Amount (Dataset Currency Units)")

        ax.tick_params(axis="x", rotation=45)

        ax.legend()
        ax.grid(alpha=0.3)

        fig.tight_layout()
        self.add_chart(story, fig)

        # --------------------------------
        # 4. QUARTERLY FINANCIAL TRENDS
        # --------------------------------

        story.append(
            Paragraph(
                "Quarterly Financial Trends",
                heading_style
            )
        )

        quarterly = self.analytics_service.calculate_quarterly_trends(df)

        quarterly_rows = []

        for item in quarterly:

            quarterly_rows.append([
                item["quarter"],
                f'{item["revenue"]:,.2f}',
                f'{item["profit"]:,.2f}',
                f'{item["revenue_growth_percentage"]:.2f}%'
            ])

        story.append(
            self.create_table(
                [
                    "Quarter",
                    "Revenue",
                    "Profit",
                    "Revenue Growth"
                ],
                quarterly_rows
            )
        )

        story.append(Spacer(1, 5))

        # --------------------------------
        # CHART 6: QUARTERLY REVENUE AND PROFIT
        # --------------------------------

        quarters = [
            item["quarter"]
            for item in quarterly
        ]

        quarterly_revenue = [
            item["revenue"]
            for item in quarterly
        ]

        quarterly_profit = [
            item["profit"]
            for item in quarterly
        ]

        fig, ax = plt.subplots(figsize=(8, 4))

        x = range(len(quarters))
        width = 0.35

        ax.bar(
            [i - width / 2 for i in x],
            quarterly_revenue,
            width,
            label="Revenue"
        )

        ax.bar(
            [i + width / 2 for i in x],
            quarterly_profit,
            width,
            label="Profit"
        )

        ax.set_xticks(list(x))
        ax.set_xticklabels(quarters)

        ax.set_title("Quarterly Revenue and Profit")
        ax.set_ylabel("Amount (Dataset Currency Units)")

        ax.legend()
        ax.grid(axis="y", alpha=0.3)

        fig.tight_layout()
        self.add_chart(story, fig)

        # --------------------------------
        # 5. FINANCIAL FORECASTING
        # --------------------------------

        story.append(PageBreak())

        story.append(
            Paragraph(
                "Financial Forecasting",
                heading_style
            )
        )

        forecast = self.forecasting_service.generate_forecasts(
            df,
            forecast_periods=3
        )

        forecast_configs = [
            (
                "revenue_forecast",
                "Revenue Forecast",
                "revenue"
            ),
            (
                "profit_forecast",
                "Profit Forecast",
                "profit"
            )
        ]

        # --------------------------------
        # FORECAST TABLES AND CHART 7
        # --------------------------------

        for key, title, metric in forecast_configs:

            result = forecast[key]

            story.append(
                Paragraph(
                    title,
                    styles["Heading3"]
                )
            )

            story.append(
                Paragraph(
                    f'Selected Model: {result["selected_model"]}',
                    styles["Normal"]
                )
            )

            evaluation = result["evaluation"]

            story.append(
                Paragraph(
                    f'MAE: {evaluation["mae"]:,.2f} | '
                    f'RMSE: {evaluation["rmse"]:,.2f} | '
                    f'MAPE: {evaluation["mape_percentage"]}%',
                    styles["Normal"]
                )
            )

            forecast_rows = []

            for item in result["forecast"]:

                forecast_rows.append([
                    item["month"],
                    f'{item["predicted_value"]:,.2f}'
                ])

            story.append(
                self.create_table(
                    ["Forecast Month", "Predicted Value"],
                    forecast_rows
                )
            )

            story.append(Spacer(1, 5))

            # Historical data

            historical_months = [
                item["month"]
                for item in monthly_data
            ]

            if metric == "revenue":

                historical_values = [
                    item["revenue"]
                    for item in monthly_data
                ]

            else:

                historical_values = [
                    item["profit"]
                    for item in monthly_data
                ]

            # Forecast data

            future_months = [
                item["month"]
                for item in result["forecast"]
            ]

            future_values = [
                item["predicted_value"]
                for item in result["forecast"]
            ]

            # Combined chart positions

            all_months = historical_months + future_months

            historical_x = list(range(len(historical_months)))

            forecast_x = list(
                range(
                    len(historical_months) - 1,
                    len(all_months)
                )
            )

            forecast_y = [
                historical_values[-1]
            ] + future_values

            fig, ax = plt.subplots(figsize=(9, 4))

            ax.plot(
                historical_x,
                historical_values,
                marker="o",
                label="Historical"
            )

            ax.plot(
                forecast_x,
                forecast_y,
                marker="o",
                linestyle="--",
                label="Forecast"
            )

            ax.axvline(
                len(historical_months) - 1,
                linestyle=":",
                alpha=0.7
            )

            ax.set_xticks(list(range(len(all_months))))
            ax.set_xticklabels(all_months, rotation=45)

            ax.set_title(
                f"Historical vs Forecasted {metric.capitalize()}"
            )

            ax.set_xlabel("Month")
            ax.set_ylabel("Amount (Dataset Currency Units)")

            ax.legend()
            ax.grid(alpha=0.3)

            fig.tight_layout()

            self.add_chart(story, fig)

        # --------------------------------
        # REPORT NOTE
        # --------------------------------

        story.append(Spacer(1, 15))

        story.append(
            Paragraph(
                "Note: Forecasts are based on historical dataset observations. "
                "They should not be interpreted as guaranteed future results. "
                "All financial values use the dataset's original currency units.",
                styles["Italic"]
            )
        )

        # --------------------------------
        # BUILD PDF
        # --------------------------------

        document.build(story)

        buffer.seek(0)

        return buffer.getvalue()
