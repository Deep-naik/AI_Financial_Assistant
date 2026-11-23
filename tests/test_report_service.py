
import pandas as pd

from app.services.report_service import FinancialReportService


df = pd.read_csv(
    "data/processed/financial_sample_cleaned.csv",
    parse_dates=["date"]
)

report_service = FinancialReportService()

pdf_content = report_service.generate_report(
    df,
    "5b6feaf1-1e30-4ada-a821-d322961a70df"
)

output_path = "reports/financial_intelligence_report.pdf"

with open(output_path, "wb") as file:
    file.write(pdf_content)

print("PDF report generated successfully!")
print("Output:", output_path)
print("File size:", len(pdf_content), "bytes")
