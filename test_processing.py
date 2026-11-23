
from app.services.data_service import DataProcessingService

service = DataProcessingService()

file_path = "data/sample/Financial Sample.xlsx"

# Load original data
df = service.load_file(file_path)

print("Original dataset:", df.shape)

# Clean data
cleaned_df, report = service.clean_data(df)

print("\n--- CLEANED DATASET ---")
print(cleaned_df.head())

print("\n--- CLEANED COLUMNS ---")
print(cleaned_df.columns.tolist())

print("\n--- DATA QUALITY REPORT ---")

for key, value in report.items():
    print(f"{key}: {value}")

# Save processed data
cleaned_df.to_csv(
    "data/processed/financial_sample_cleaned.csv",
    index=False
)

print("\nProcessed dataset saved successfully.")
