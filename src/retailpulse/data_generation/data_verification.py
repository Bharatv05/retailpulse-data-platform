import pandas as pd
# customer_df = pd.read_csv("data\source\customers\customers.csv") # column name for reference ['customer_id', 'customer_name', 'email', 'phone', 'city', 'state', 'country', 'signup_date', 'customer_status', 'created_at', 'updated_at']
# print("\n--- Customer Data Validation ---")
# print("Rows:", len(customer_df))
# print(
#     "Customer ID unique:",
#     customer_df["customer_id"].is_unique
# )
# print(
#     "Any NULL:",
#     customer_df.isnull().any().any()
# )
# print(
#     "Invalid timestamps:",
#     (
#         pd.to_datetime(customer_df["updated_at"])
#         < pd.to_datetime(customer_df["created_at"])
#     ).sum()
# )
# print(
#     "Non-India customers:",
#     (customer_df["country"] != "India").sum()
# )
# print(
#     "Customer status values:",
#     customer_df["customer_status"].unique()
# )

import pandas as pd
from retailpulse.data_generation.config import PRODUCT_CATALOG, CATEGORY_PRICE_RANGES

df = pd.read_csv("data/source/products/products.csv")

# ── Row Count ─────────────────────────────────────────────────────────────────
print("Row count          :", len(df))

# ── Product ID Uniqueness ─────────────────────────────────────────────────────
print("Unique product IDs :", df["product_id"].is_unique)
print("Duplicate IDs      :", df["product_id"].duplicated().sum())

# ── NULLs ─────────────────────────────────────────────────────────────────────
print("Any NULLs          :", df.isnull().any().any())
print(df.isnull().sum())

# ── Price Validity ────────────────────────────────────────────────────────────
print("Zero/negative price:", (df["unit_price"] <= 0).sum())

# ── Discount Validity ─────────────────────────────────────────────────────────
print("Invalid discounts  :", ((df["discount_percentage"] < 0) | (df["discount_percentage"] > 100)).sum())

# ── Status Validity ───────────────────────────────────────────────────────────
print("Status values      :", df["product_status"].unique())
print("Invalid statuses   :", (~df["product_status"].isin(["ACTIVE", "DISCONTINUED"])).sum())

# ── Category / Subcategory Consistency ───────────────────────────────────────
def is_valid_pair(row):
    return row["subcategory"] in PRODUCT_CATALOG.get(row["category"], [])

invalid_pairs = df.apply(is_valid_pair, axis=1)
print("Invalid cat/subcat :", (~invalid_pairs).sum())

# ── Timestamp Validity ────────────────────────────────────────────────────────
df["created_at"] = pd.to_datetime(df["created_at"])
df["updated_at"] = pd.to_datetime(df["updated_at"])
print("updated_at < created_at:", (df["updated_at"] < df["created_at"]).sum())

# ── Status Distribution ───────────────────────────────────────────────────────
print("\nStatus distribution:")
print(df["product_status"].value_counts())

# ── Category Distribution ─────────────────────────────────────────────────────
print("\nCategory distribution:")
print(df["category"].value_counts())