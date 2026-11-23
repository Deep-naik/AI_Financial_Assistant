
import pandas as pd

df = pd.read_excel("data/sample/Financial Sample.xlsx")

# Check records with missing Discount Band
missing = df[df["Discount Band"].isna()]

print("Missing Discount Band records:", len(missing))

print("\nDiscount values in missing records:")
print(missing["Discounts"].value_counts(dropna=False))

print("\nDiscount Band vs Discount:")
print(
    df.groupby("Discount Band", dropna=False)["Discounts"]
    .agg(["count", "min", "max", "mean"])
)

print("\nSample missing records:")
print(
    missing[
        ["Product", "Discounts", " Sales", "Profit"]
    ].head(10)
)
