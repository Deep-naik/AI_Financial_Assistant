
from frontend.utils.api import (
    check_backend,
    fetch_datasets
)

print("Backend connected:", check_backend())

datasets = fetch_datasets()

print("\nAvailable datasets:")

if datasets:
    for dataset in datasets:
        print(
            dataset["filename"],
            "|",
            dataset["dataset_id"]
        )
else:
    print("No datasets found or backend unavailable.")
