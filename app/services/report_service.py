from io import BytesIO
from datetime import datetime
from xml.sax.saxutils import escape

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    Image,
    KeepTogether,
)

from app.services.analytics_service import FinancialAnalyticsService
from app.services.forecasting_service import FinancialForecastingService


class NumberedCanvas(canvas.Canvas):
    """Canvas that adds page numbers after the document has been built."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        page_count = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(page_count)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        page_number = self._pageNumber
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#666666"))
        self.drawString(30, 18, "AI Financial Intelligence")
        self.drawRightString(
            A4[0] - 30,
            18,
            f"Page {page_number} of {page_count}",
        )
        self.setStrokeColor(colors.HexColor("#D9E2F3"))
        self.line(30, 27, A4[0] - 30, 27)
        self.restoreState()


class FinancialReportService:

    def __init__(self):
        self.analytics_service = FinancialAnalyticsService()
        self.forecasting_service = FinancialForecastingService()

    # ---------------------------------------------------------
    # FORMATTING HELPERS
    # ---------------------------------------------------------

    def add_section_text(self, story, text, styles):
        story.append(
            Paragraph(
                escape(str(text)),
                styles["ReportBody"],
            )
        )
        story.append(Spacer(1, 5))

    def add_bullet_points(self, story, points, styles):
        for point in points:
            story.append(
                Paragraph(
                    f"&bull;&nbsp; {escape(str(point))}",
                    styles["ReportBody"],
                )
            )
            story.append(Spacer(1, 3))

    def add_chart(self, story, figure, width=6.7 * inch, height=2.9 * inch):
        chart_buffer = BytesIO()
        figure.savefig(
            chart_buffer,
            format="png",
            dpi=160,
            bbox_inches="tight",
        )
        chart_buffer.seek(0)

        story.append(
            Image(
                chart_buffer,
                width=width,
                height=height,
                kind="proportional",
            )
        )
        story.append(Spacer(1, 7))
        plt.close(figure)

    def create_table(self, headers, rows):
        table_data = [headers] + rows
        table = Table(
            table_data,
            repeatRows=1,
            hAlign="LEFT",
        )
        table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#17365D")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 7),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                (
                    "ROWBACKGROUNDS",
                    (0, 1),
                    (-1, -1),
                    [colors.white, colors.HexColor("#EAF0F8")],
                ),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
            ])
        )
        return table

    def money(self, value):
        return f"{float(value):,.2f}"

    def add_section_heading(self, story, text, style):
        story.append(Paragraph(escape(text), style))
        story.append(Spacer(1, 4))

    # ---------------------------------------------------------
    # INTERPRETATION HELPERS
    # ---------------------------------------------------------

    def get_dimension_extremes(self, analysis):
        results = analysis.get("results", [])
        if not results:
            return None, None, None, None

        highest_profit = max(results, key=lambda x: x.get("profit", 0))
        lowest_profit = min(results, key=lambda x: x.get("profit", 0))
        highest_margin = max(
            results,
            key=lambda x: x.get("profit_margin_percentage", 0),
        )
        lowest_margin = min(
            results,
            key=lambda x: x.get("profit_margin_percentage", 0),
        )
        return highest_profit, lowest_profit, highest_margin, lowest_margin

    def build_executive_summary(self, kpis, segment_analysis):
        financial = kpis["financial_kpis"]
        profitability = kpis["profitability"]
        total_records = kpis["total_records"]

        revenue = financial["total_sales"]
        profit = financial["total_profit"]
        margin = financial["profit_margin_percentage"]
        loss_records = profitability["loss_making_records"]

        highest_profit, lowest_profit, highest_margin, _ = (
            self.get_dimension_extremes(segment_analysis)
        )

        paragraphs = [
            (
                f"The dataset contains {total_records:,} financial records, "
                f"with total revenue of {self.money(revenue)} and total profit "
                f"of {self.money(profit)}. The overall profit margin is "
                f"{margin:.2f}%."
            ),
            (
                f"{profitability['profitable_records']:,} records are profitable, "
                f"{loss_records:,} are loss-making and "
                f"{profitability['zero_profit_records']:,} have zero profit."
            ),
        ]

        if highest_profit:
            paragraphs.append(
                f"The {highest_profit['name']} segment contributes the highest "
                f"absolute profit ({self.money(highest_profit['profit'])})."
            )

        if highest_margin:
            paragraphs.append(
                f"The {highest_margin['name']} segment has the highest profit "
                f"margin ({highest_margin['profit_margin_percentage']:.2f}%). "
                "A high margin and the highest total profit are different "
                "measures of performance."
            )

        if lowest_profit and lowest_profit["profit"] < 0:
            paragraphs.append(
                f"The {lowest_profit['name']} segment is loss-making, with a "
                f"reported profit of {self.money(lowest_profit['profit'])}. "
                "This segment deserves further investigation."
            )

        return paragraphs

    def build_dimension_insights(self, title, analysis):
        results = analysis.get("results", [])
        if not results:
            return [f"No {title.lower()} analysis results were available."]

        highest_profit, lowest_profit, highest_margin, lowest_margin = (
            self.get_dimension_extremes(analysis)
        )

        insights = []

        if highest_profit:
            insights.append(
                f"{highest_profit['name']} generated the highest total profit "
                f"({self.money(highest_profit['profit'])}) among the "
                f"{title.lower()} categories."
            )

        if lowest_profit:
            insights.append(
                f"{lowest_profit['name']} generated the lowest total profit "
                f"({self.money(lowest_profit['profit'])})."
            )

        if highest_margin:
            insights.append(
                f"{highest_margin['name']} recorded the highest profit margin "
                f"({highest_margin['profit_margin_percentage']:.2f}%)."
            )

        if lowest_margin and lowest_margin["name"] != (
            highest_margin["name"] if highest_margin else None
        ):
            insights.append(
                f"{lowest_margin['name']} recorded the lowest profit margin "
                f"({lowest_margin['profit_margin_percentage']:.2f}%)."
            )

        loss_categories = [
            item for item in results if item.get("loss_records", 0) > 0
        ]
        if loss_categories:
            names = ", ".join(
                f"{item['name']} ({item['loss_records']} loss records)"
                for item in loss_categories
            )
            insights.append(
                f"Categories with loss-making records include: {names}."
            )

        return insights

    def build_monthly_insights(self, monthly_data):
        if not monthly_data:
            return ["Monthly trend data was not available."]

        highest_revenue = max(monthly_data, key=lambda x: x["revenue"])
        lowest_revenue = min(monthly_data, key=lambda x: x["revenue"])
        highest_profit = max(monthly_data, key=lambda x: x["profit"])

        return [
            (
                f"The highest-revenue month was {highest_revenue['month']}, "
                f"with revenue of {self.money(highest_revenue['revenue'])}."
            ),
            (
                f"The lowest-revenue month was {lowest_revenue['month']}, "
                f"with revenue of {self.money(lowest_revenue['revenue'])}."
            ),
            (
                f"The highest monthly profit occurred in "
                f"{highest_profit['month']} "
                f"({self.money(highest_profit['profit'])})."
            ),
            (
                "Monthly values fluctuate across the observation period. "
                "These movements describe the historical dataset and do not "
                "by themselves establish the causes of the changes."
            ),
        ]

    def build_quarterly_insights(self, quarterly_data):
        if not quarterly_data:
            return ["Quarterly trend data was not available."]

        highest_revenue = max(quarterly_data, key=lambda x: x["revenue"])
        lowest_revenue = min(quarterly_data, key=lambda x: x["revenue"])

        return [
            (
                f"{highest_revenue['quarter']} recorded the highest quarterly "
                f"revenue ({self.money(highest_revenue['revenue'])})."
            ),
            (
                f"{lowest_revenue['quarter']} recorded the lowest quarterly "
                f"revenue ({self.money(lowest_revenue['revenue'])})."
            ),
            (
                "Quarterly growth rates should be interpreted with care, "
                "particularly where the first quarter represents only a "
                "partial period in the dataset."
            ),
        ]

    # ---------------------------------------------------------
    # MAIN REPORT GENERATION
    # ---------------------------------------------------------

    def generate_report(self, df, dataset_id):
        buffer = BytesIO()

        document = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=30,
            leftMargin=30,
            topMargin=38,
            bottomMargin=38,
            title="Financial Intelligence Report",
            author="AI Financial Intelligence",
        )

        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            "ReportTitle",
            parent=styles["Title"],
            alignment=TA_CENTER,
            textColor=colors.HexColor("#17365D"),
            fontSize=21,
            leading=26,
            spaceAfter=12,
        )

        subtitle_style = ParagraphStyle(
            "ReportSubtitle",
            parent=styles["Normal"],
            alignment=TA_CENTER,
            fontSize=10,
            textColor=colors.HexColor("#555555"),
            spaceAfter=8,
        )

        heading_style = ParagraphStyle(
            "SectionHeading",
            parent=styles["Heading2"],
            textColor=colors.HexColor("#17365D"),
            fontSize=13,
            leading=16,
            spaceBefore=10,
            spaceAfter=6,
        )

        subheading_style = ParagraphStyle(
            "SubSectionHeading",
            parent=styles["Heading3"],
            textColor=colors.HexColor("#24476B"),
            fontSize=10,
            leading=13,
            spaceBefore=7,
            spaceAfter=4,
        )

        body_style = ParagraphStyle(
            "ReportBody",
            parent=styles["Normal"],
            fontSize=8.8,
            leading=13,
            alignment=TA_LEFT,
            spaceAfter=5,
        )
        styles.add(body_style)

        small_style = ParagraphStyle(
            "SmallNote",
            parent=styles["Italic"],
            fontSize=8,
            leading=11,
            textColor=colors.HexColor("#555555"),
        )

        story = []

        # -----------------------------------------------------
        # CALCULATE DATA
        # -----------------------------------------------------

        kpis = self.analytics_service.calculate_kpis(df)
        financial = kpis["financial_kpis"]
        averages = kpis["averages"]
        profitability = kpis["profitability"]

        dimension_analyses = {
            "product": self.analytics_service.calculate_dimension_analysis(
                df, "product"
            ),
            "country": self.analytics_service.calculate_dimension_analysis(
                df, "country"
            ),
            "segment": self.analytics_service.calculate_dimension_analysis(
                df, "segment"
            ),
        }

        monthly = self.analytics_service.calculate_monthly_trends(df)
        monthly_data = monthly["monthly_trends"]
        quarterly = self.analytics_service.calculate_quarterly_trends(df)

        # The forecasting service supports multiple horizons.
        # Generate a full 12-month forecast for the PDF.
        forecast = self.forecasting_service.generate_forecasts(
            df,
            forecast_periods=12,
        )

        # -----------------------------------------------------
        # COVER PAGE
        # -----------------------------------------------------

        story.append(Spacer(1, 0.65 * inch))
        story.append(
            Paragraph("Financial Intelligence Report", title_style)
        )
        story.append(
            Paragraph(
                "AI-Powered Business Intelligence and Decision Support System",
                subtitle_style,
            )
        )
        story.append(Spacer(1, 15))

        cover_rows = [
            ["Dataset ID", str(dataset_id)],
            [
                "Report Generated",
                datetime.now().strftime("%d-%m-%Y %H:%M"),
            ],
            ["Total Records", f"{kpis['total_records']:,}"],
            ["Reporting Currency", "Original currency units in the dataset"],
        ]
        story.append(self.create_table(["Report Detail", "Value"], cover_rows))
        story.append(Spacer(1, 22))

        story.append(
            Paragraph(
                "Purpose of this Report",
                heading_style,
            )
        )
        self.add_section_text(
            story,
            (
                "This report presents a descriptive and diagnostic analysis "
                "of the selected financial dataset, including key performance "
                "indicators, product and country performance, segment "
                "profitability, historical trends and statistical forecasts. "
                "The report combines numerical summaries, charts and written "
                "interpretations to support business decision-making."
            ),
            styles,
        )

        story.append(PageBreak())

        # -----------------------------------------------------
        # TABLE OF CONTENTS
        # -----------------------------------------------------

        self.add_section_heading(story, "Contents", heading_style)
        contents = [
            ["1", "Executive Summary", "3"],
            ["2", "Overall Financial Performance", "3"],
            ["3", "Product Performance Analysis", "4"],
            ["4", "Country Performance Analysis", "5"],
            ["5", "Segment Performance and Risk Analysis", "6"],
            ["6", "Monthly Financial Trends", "7"],
            ["7", "Quarterly Financial Trends", "8"],
            ["8", "Financial Forecasting", "9–10"],
            ["9", "Business Recommendations", "11"],
            ["10", "Methodology and Limitations", "12"],
        ]
        story.append(
            self.create_table(["Section", "Description", "Page"], contents)
        )
        story.append(PageBreak())

        # -----------------------------------------------------
        # 1. EXECUTIVE SUMMARY
        # -----------------------------------------------------

        self.add_section_heading(
            story,
            "1. Executive Summary",
            heading_style,
        )

        for paragraph in self.build_executive_summary(
            kpis,
            dimension_analyses["segment"],
        ):
            self.add_section_text(story, paragraph, styles)

        # -----------------------------------------------------
        # 2. OVERALL FINANCIAL PERFORMANCE
        # -----------------------------------------------------

        self.add_section_heading(
            story,
            "2. Overall Financial Performance",
            heading_style,
        )

        kpi_rows = [
            ["Total Records", f"{kpis['total_records']:,}"],
            ["Total Revenue", self.money(financial["total_sales"])],
            ["Total Profit", self.money(financial["total_profit"])],
            ["Total COGS", self.money(financial["total_cogs"])],
            ["Total Discounts", self.money(financial["total_discounts"])],
            ["Units Sold", f"{financial['total_units_sold']:,.0f}"],
            [
                "Profit Margin",
                f"{financial['profit_margin_percentage']:.2f}%",
            ],
            [
                "Average Revenue per Record",
                self.money(averages["average_sales_per_record"]),
            ],
            [
                "Average Profit per Record",
                self.money(averages["average_profit_per_record"]),
            ],
            [
                "Profitable Records",
                f"{profitability['profitable_records']:,}",
            ],
            [
                "Loss-Making Records",
                f"{profitability['loss_making_records']:,}",
            ],
            [
                "Zero-Profit Records",
                f"{profitability['zero_profit_records']:,}",
            ],
        ]

        story.append(
            self.create_table(["Financial Indicator", "Value"], kpi_rows)
        )
        story.append(Spacer(1, 8))

        self.add_section_text(
            story,
            (
                f"The business generated total revenue of "
                f"{self.money(financial['total_sales'])} and total profit "
                f"of {self.money(financial['total_profit'])}. The overall "
                f"profit margin was "
                f"{financial['profit_margin_percentage']:.2f}%. Cost of "
                f"Goods Sold (COGS) amounted to "
                f"{self.money(financial['total_cogs'])}, while discounts "
                f"totalled {self.money(financial['total_discounts'])}."
            ),
            styles,
        )

        self.add_section_text(
            story,
            (
                f"Out of {kpis['total_records']:,} records, "
                f"{profitability['profitable_records']:,} were profitable "
                f"and {profitability['loss_making_records']:,} were "
                f"loss-making. The presence of loss-making records indicates "
                "that overall profitability does not mean every transaction "
                "or business category is profitable."
            ),
            styles,
        )

        fig, ax = plt.subplots(figsize=(8, 3.4))
        categories = ["Revenue", "COGS", "Profit"]
        values = [
            financial["total_sales"],
            financial["total_cogs"],
            financial["total_profit"],
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
                va="bottom",
                fontsize=8,
            )
        fig.tight_layout()
        self.add_chart(story, fig, height=2.5 * inch)

        # -----------------------------------------------------
        # 3-5. PRODUCT, COUNTRY AND SEGMENT ANALYSIS
        # -----------------------------------------------------

        dimension_configs = [
            ("3. Product Performance Analysis", "Product", "product"),
            ("4. Country Performance Analysis", "Country", "country"),
            ("5. Segment Performance and Risk Analysis", "Segment", "segment"),
        ]

        for section_title, display_name, dimension in dimension_configs:
            analysis = dimension_analyses[dimension]
            results = analysis.get("results", [])

            # Let the first dimension section flow naturally after the KPI page.
            # This avoids creating a blank page when the previous content ends
            # close to a page boundary. Later dimension sections start cleanly.
            if dimension != "product":
                story.append(PageBreak())
            self.add_section_heading(story, section_title, heading_style)

            rows = []
            for item in results:
                rows.append([
                    str(item["name"]),
                    self.money(item["revenue"]),
                    self.money(item["profit"]),
                    f"{item['profit_margin_percentage']:.2f}%",
                    str(item.get("loss_records", 0)),
                ])

            story.append(
                self.create_table(
                    [
                        display_name,
                        "Revenue",
                        "Profit",
                        "Margin",
                        "Loss Records",
                    ],
                    rows,
                )
            )
            story.append(Spacer(1, 7))

            insights = self.build_dimension_insights(
                display_name,
                analysis,
            )
            self.add_section_heading(
                story,
                "Key Findings and Interpretation",
                subheading_style,
            )
            self.add_bullet_points(story, insights, styles)

            if dimension == "product":
                names = [item["name"] for item in results]
                revenues = [item["revenue"] for item in results]
                profits = [item["profit"] for item in results]

                fig, ax = plt.subplots(figsize=(8, 4))
                x = range(len(names))
                width = 0.35
                ax.bar(
                    [i - width / 2 for i in x],
                    revenues,
                    width,
                    label="Revenue",
                )
                ax.bar(
                    [i + width / 2 for i in x],
                    profits,
                    width,
                    label="Profit",
                )
                ax.set_xticks(list(x))
                ax.set_xticklabels(names)
                ax.set_title("Product-wise Revenue and Profit")
                ax.set_ylabel("Amount (Dataset Currency Units)")
                ax.legend()
                ax.grid(axis="y", alpha=0.3)
                fig.tight_layout()
                self.add_chart(story, fig)

            elif dimension == "country":
                countries = [item["name"] for item in results]
                revenues = [item["revenue"] for item in results]

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
                        va="center",
                        fontsize=8,
                    )

                fig.tight_layout()
                self.add_chart(story, fig)

            elif dimension == "segment":
                segments = [item["name"] for item in results]
                margins = [
                    item["profit_margin_percentage"] for item in results
                ]

                fig, ax = plt.subplots(figsize=(8, 4))
                bars = ax.barh(segments, margins)
                ax.axvline(0, linewidth=1, color="black")
                ax.set_title("Segment-wise Profit Margin")
                ax.set_xlabel("Profit Margin (%)")
                ax.invert_yaxis()
                ax.grid(axis="x", alpha=0.3)
                ax.margins(x=0.20)

                for bar, value in zip(bars, margins):
                    ax.annotate(
                        f"{value:.2f}%",
                        xy=(
                            value,
                            bar.get_y() + bar.get_height() / 2,
                        ),
                        xytext=(5 if value >= 0 else -5, 0),
                        textcoords="offset points",
                        va="center",
                        ha="left" if value >= 0 else "right",
                        fontsize=8,
                    )

                fig.tight_layout()
                self.add_chart(story, fig)

                # Segment-specific risk observations
                loss_segments = [
                    item for item in results
                    if item.get("profit", 0) < 0
                ]
                if loss_segments:
                    self.add_section_heading(
                        story,
                        "Financial Risk Observations",
                        subheading_style,
                    )
                    risk_points = []
                    for item in loss_segments:
                        risk_points.append(
                            f"{item['name']} has a negative profit of "
                            f"{self.money(item['profit'])} and a margin of "
                            f"{item['profit_margin_percentage']:.2f}%. "
                            f"It contains {item.get('loss_records', 0)} "
                            "loss-making records."
                        )
                    self.add_bullet_points(story, risk_points, styles)

        # -----------------------------------------------------
        # 6. MONTHLY FINANCIAL TRENDS
        # -----------------------------------------------------

        story.append(PageBreak())
        self.add_section_heading(
            story,
            "6. Monthly Financial Trends",
            heading_style,
        )

        monthly_rows = [
            [
                item["month"],
                self.money(item["revenue"]),
                self.money(item["profit"]),
            ]
            for item in monthly_data
        ]
        story.append(
            self.create_table(
                ["Month", "Revenue", "Profit"],
                monthly_rows,
            )
        )

        self.add_section_heading(
            story,
            "Monthly Trend Interpretation",
            subheading_style,
        )
        self.add_bullet_points(
            story,
            self.build_monthly_insights(monthly_data),
            styles,
        )

        months = [item["month"] for item in monthly_data]
        monthly_revenue = [item["revenue"] for item in monthly_data]
        monthly_profit = [item["profit"] for item in monthly_data]

        fig, ax = plt.subplots(figsize=(9, 4))
        ax.plot(
            months,
            monthly_revenue,
            marker="o",
            label="Revenue",
        )
        ax.plot(
            months,
            monthly_profit,
            marker="s",
            label="Profit",
        )
        ax.set_title("Monthly Revenue and Profit Trends")
        ax.set_xlabel("Month")
        ax.set_ylabel("Amount (Dataset Currency Units)")
        ax.tick_params(axis="x", rotation=45)
        ax.legend()
        ax.grid(alpha=0.3)
        fig.tight_layout()
        self.add_chart(story, fig)

        # -----------------------------------------------------
        # 7. QUARTERLY FINANCIAL TRENDS
        # -----------------------------------------------------

        story.append(PageBreak())
        self.add_section_heading(
            story,
            "7. Quarterly Financial Trends",
            heading_style,
        )

        quarterly_rows = [
            [
                item["quarter"],
                self.money(item["revenue"]),
                self.money(item["profit"]),
                f"{item['revenue_growth_percentage']:.2f}%",
            ]
            for item in quarterly
        ]
        story.append(
            self.create_table(
                ["Quarter", "Revenue", "Profit", "Revenue Growth"],
                quarterly_rows,
            )
        )

        self.add_section_heading(
            story,
            "Quarterly Trend Interpretation",
            subheading_style,
        )
        self.add_bullet_points(
            story,
            self.build_quarterly_insights(quarterly),
            styles,
        )

        quarters = [item["quarter"] for item in quarterly]
        quarterly_revenue = [item["revenue"] for item in quarterly]
        quarterly_profit = [item["profit"] for item in quarterly]

        fig, ax = plt.subplots(figsize=(8, 4))
        x = range(len(quarters))
        width = 0.35
        ax.bar(
            [i - width / 2 for i in x],
            quarterly_revenue,
            width,
            label="Revenue",
        )
        ax.bar(
            [i + width / 2 for i in x],
            quarterly_profit,
            width,
            label="Profit",
        )
        ax.set_xticks(list(x))
        ax.set_xticklabels(quarters)
        ax.set_title("Quarterly Revenue and Profit")
        ax.set_ylabel("Amount (Dataset Currency Units)")
        ax.legend()
        ax.grid(axis="y", alpha=0.3)
        fig.tight_layout()
        self.add_chart(story, fig)

        # -----------------------------------------------------
        # 8. FINANCIAL FORECASTING
        # -----------------------------------------------------

        story.append(PageBreak())
        self.add_section_heading(
            story,
            "8. Financial Forecasting",
            heading_style,
        )

        self.add_section_text(
            story,
            (
                "The forecasting section presents a 12-month projection "
                "generated from the historical observations available in "
                "the dataset. Forecasts are model-based estimates and should "
                "not be interpreted as guaranteed future outcomes."
            ),
            styles,
        )

        forecast_configs = [
            ("revenue_forecast", "Revenue Forecast", "revenue"),
            ("profit_forecast", "Profit Forecast", "profit"),
        ]

        for forecast_index, (key, title, metric) in enumerate(forecast_configs):
            # Put revenue and profit forecasts on separate pages so each
            # forecast table and chart stays together more reliably.
            if forecast_index > 0:
                story.append(PageBreak())

            result = forecast[key]

            self.add_section_heading(
                story,
                title,
                subheading_style,
            )

            story.append(
                Paragraph(
                    f"Selected Model: "
                    f"{escape(str(result['selected_model']))}",
                    styles["ReportBody"],
                )
            )

            evaluation = result["evaluation"]
            story.append(
                Paragraph(
                    f"MAE: {evaluation['mae']:,.2f} &nbsp; | &nbsp; "
                    f"RMSE: {evaluation['rmse']:,.2f} &nbsp; | &nbsp; "
                    f"MAPE: {evaluation['mape_percentage']}%",
                    styles["ReportBody"],
                )
            )

            forecast_rows = [
                [
                    item["month"],
                    self.money(item["predicted_value"]),
                ]
                for item in result["forecast"]
            ]
            story.append(
                self.create_table(
                    ["Forecast Month", "Predicted Value"],
                    forecast_rows,
                )
            )
            story.append(Spacer(1, 7))

            historical_months = [
                item["month"] for item in monthly_data
            ]
            if metric == "revenue":
                historical_values = [
                    item["revenue"] for item in monthly_data
                ]
            else:
                historical_values = [
                    item["profit"] for item in monthly_data
                ]

            future_months = [
                item["month"] for item in result["forecast"]
            ]
            future_values = [
                item["predicted_value"] for item in result["forecast"]
            ]

            all_months = historical_months + future_months
            historical_x = list(range(len(historical_months)))
            forecast_x = list(
                range(len(historical_months) - 1, len(all_months))
            )
            forecast_y = [historical_values[-1]] + future_values

            fig, ax = plt.subplots(figsize=(9, 4))
            ax.plot(
                historical_x,
                historical_values,
                marker="o",
                label="Historical",
            )
            ax.plot(
                forecast_x,
                forecast_y,
                marker="o",
                linestyle="--",
                label="Forecast",
            )
            ax.axvline(
                len(historical_months) - 1,
                linestyle=":",
                alpha=0.7,
            )
            ax.set_xticks(list(range(len(all_months))))
            ax.set_xticklabels(all_months, rotation=60, fontsize=7)
            ax.set_title(
                f"Historical vs Forecasted {metric.capitalize()}"
            )
            ax.set_xlabel("Month")
            ax.set_ylabel("Amount (Dataset Currency Units)")
            ax.legend()
            ax.grid(alpha=0.3)
            fig.tight_layout()
            self.add_chart(story, fig, height=3.2 * inch)

        # -----------------------------------------------------
        # 9. BUSINESS RECOMMENDATIONS
        # -----------------------------------------------------

        story.append(PageBreak())
        self.add_section_heading(
            story,
            "9. Business Recommendations",
            heading_style,
        )

        segment_results = dimension_analyses["segment"].get("results", [])
        recommendations = []

        loss_segments = [
            item for item in segment_results
            if item.get("profit", 0) < 0
        ]
        if loss_segments:
            for item in loss_segments:
                recommendations.append(
                    f"Investigate the {item['name']} segment's negative "
                    f"profit ({self.money(item['profit'])}). Review pricing, "
                    "discounting, product mix and cost allocation to identify "
                    "the factors associated with the losses. The dataset "
                    "shows the loss, but does not independently establish "
                    "its underlying cause."
                )

        low_margin_segments = [
            item for item in segment_results
            if (
                item.get("profit_margin_percentage", 0)
                < financial["profit_margin_percentage"]
                and item.get("profit", 0) >= 0
            )
        ]
        for item in low_margin_segments:
            recommendations.append(
                f"Review the {item['name']} segment's profitability. Its "
                f"margin of {item['profit_margin_percentage']:.2f}% is below "
                f"the overall margin of "
                f"{financial['profit_margin_percentage']:.2f}%. Examine "
                "discount policies, pricing and cost drivers before setting "
                "specific improvement targets."
            )

        highest_profit, _, highest_margin, _ = self.get_dimension_extremes(
            dimension_analyses["segment"]
        )
        if highest_profit:
            recommendations.append(
                f"Study the practices and revenue drivers of the "
                f"{highest_profit['name']} segment, which generated the "
                f"highest absolute segment profit "
                f"({self.money(highest_profit['profit'])}), to identify "
                "practices that may be transferable to other segments."
            )

        if highest_margin:
            recommendations.append(
                f"Evaluate opportunities to grow the "
                f"{highest_margin['name']} segment, which recorded the "
                f"highest margin ({highest_margin['profit_margin_percentage']:.2f}%). "
                "Assess its revenue scale and whether expansion is commercially "
                "practical; the highest margin does not automatically mean "
                "the highest total profit."
            )

        recommendations.extend([
            (
                "Monitor loss-making records and segment-level margins "
                "regularly instead of relying only on aggregate profit."
            ),
            (
                "Use monthly and quarterly performance reviews to investigate "
                "large changes in revenue and profit. Validate possible "
                "business explanations with operational information before "
                "taking action."
            ),
        ])

        self.add_bullet_points(story, recommendations, styles)

        # -----------------------------------------------------
        # 10. METHODOLOGY AND LIMITATIONS
        # -----------------------------------------------------

        story.append(PageBreak())
        self.add_section_heading(
            story,
            "10. Methodology and Limitations",
            heading_style,
        )

        self.add_section_heading(
            story,
            "Methodology",
            subheading_style,
        )
        methodology = [
            (
                "Descriptive analytics: financial KPIs such as revenue, "
                "profit, COGS, discounts, units sold and profit margin are "
                "calculated from the selected dataset."
            ),
            (
                "Dimension analysis: records are grouped by product, country "
                "and segment to compare revenue, profit, profit margin and "
                "loss-making records."
            ),
            (
                "Trend analysis: monthly and quarterly revenue and profit "
                "are aggregated to examine historical patterns and changes."
            ),
            (
                "Forecasting: the forecasting service selects a model using "
                "its evaluation procedure and generates revenue and profit "
                "forecasts for the requested horizon."
            ),
            (
                "Forecast evaluation: MAE, RMSE and MAPE are reported as "
                "provided by the forecasting service. Lower error values "
                "generally indicate better predictive performance when "
                "comparing models on the same evaluation data."
            ),
        ]
        self.add_bullet_points(story, methodology, styles)

        self.add_section_heading(
            story,
            "Limitations",
            subheading_style,
        )
        limitations = [
            (
                "The analysis depends on the completeness, accuracy and "
                "coverage of the uploaded dataset."
            ),
            (
                "The dataset contains a limited historical observation "
                "period. Forecasts extrapolate from this historical data "
                "and should not be treated as current market predictions."
            ),
            (
                "Forecast accuracy may be affected by the short history, "
                "seasonality, structural changes and unexpected events."
            ),
            (
                "The dataset supports identification of financial patterns "
                "and associations, but it may not contain enough operational "
                "information to prove why a segment or transaction is "
                "performing poorly."
            ),
            (
                "All financial values are expressed in the original "
                "currency units of the dataset. No currency conversion "
                "has been applied."
            ),
        ]
        self.add_bullet_points(story, limitations, styles)

        story.append(Spacer(1, 12))
        story.append(
            Paragraph(
                "End of Report",
                ParagraphStyle(
                    "EndReport",
                    parent=styles["Normal"],
                    alignment=TA_CENTER,
                    textColor=colors.HexColor("#17365D"),
                    fontName="Helvetica-Bold",
                    fontSize=10,
                ),
            )
        )

        # -----------------------------------------------------
        # BUILD PDF
        # -----------------------------------------------------

        document.build(
            story,
            canvasmaker=NumberedCanvas,
        )

        buffer.seek(0)
        return buffer.getvalue()
