# src/retailpulse/data_generation/orders_verification.py

import pandas as pd
from pathlib import Path

# ── Load Data ──────────────────────────────────────────────────────────────────

PROJECT_ROOT   = Path(__file__).resolve().parents[3]
SOURCE_DIR     = PROJECT_ROOT / "data" / "source"

orders_df      = pd.read_csv(SOURCE_DIR / "orders"    / "orders.csv")
order_items_df = pd.read_csv(SOURCE_DIR / "orders"    / "order_items.csv")
customers_df   = pd.read_csv(SOURCE_DIR / "customers" / "customers.csv")
products_df    = pd.read_csv(SOURCE_DIR / "products"  / "products.csv")

# Parse timestamps
for df in [orders_df, order_items_df]:
    df["created_at"] = pd.to_datetime(df["created_at"])
    df["updated_at"] = pd.to_datetime(df["updated_at"])

print("=" * 60)
print("  ORDERS VERIFICATION")
print("=" * 60)

# ══════════════════════════════════════════════════════════════
# SECTION 1 — BASIC COUNTS  (provided for you as example)
# ══════════════════════════════════════════════════════════════

print("\n── Section 1: Basic Counts ──────────────────────────────")

print(f"Orders row count          : {len(orders_df):,}")
print(f"Order items row count     : {len(order_items_df):,}")
print(f"Avg items per order       : {len(order_items_df)/len(orders_df):.2f}")

# ══════════════════════════════════════════════════════════════
# SECTION 2 — UNIQUENESS  (provided for you as example)
# ══════════════════════════════════════════════════════════════

print("\n── Section 2: Uniqueness ────────────────────────────────")

print(f"Unique order_ids          : {orders_df['order_id'].is_unique}")
print(f"Duplicate order_ids       : {orders_df['order_id'].duplicated().sum()}")
print(f"Unique order_item_ids     : {order_items_df['order_item_id'].is_unique}")
print(f"Duplicate order_item_ids  : {order_items_df['order_item_id'].duplicated().sum()}")

# ══════════════════════════════════════════════════════════════
# SECTION 3 — NULL CHECKS  (provided for you as example)
# ══════════════════════════════════════════════════════════════

print("\n── Section 3: NULL Checks ───────────────────────────────")

print("Orders NULLs:")
print(orders_df.isnull().sum())

print("\nOrder Items NULLs:")
print(order_items_df.isnull().sum())

# ══════════════════════════════════════════════════════════════
# SECTION 4 — REFERENTIAL INTEGRITY
# ══════════════════════════════════════════════════════════════

print("\n── Section 4: Referential Integrity ─────────────────────")

# ✅ PROVIDED — All order customer_ids must exist in customers.csv
valid_customer_ids   = set(customers_df["customer_id"])
order_customer_ids   = set(orders_df["customer_id"])
invalid_customers    = order_customer_ids - valid_customer_ids
print(f"Customer IDs not in master: {len(invalid_customers)}")

# 🔨 TASK 4A ───────────────────────────────────────────────────
# Check that every order_id in order_items exists in orders.
#
# Hint:
#   - Get the set of order_ids from orders_df
#   - Get the set of order_ids from order_items_df
#   - Find order_ids in order_items that do NOT exist in orders
#   - Print the count — expected result: 0
#
# YOUR CODE BELOW:
# 1. Get the set of order_ids from both DataFrames
orders_ids = set(orders_df["order_id"])
order_items_ids = set(order_items_df["order_id"])

# 2. Find IDs in order_items that do NOT exist in orders (set difference)
missing_orders = order_items_ids - orders_ids

# 3. Print the count (Expected result: 0)
print(f"Missing Order Id Count: {len(missing_orders)}")


# 🔨 TASK 4B ───────────────────────────────────────────────────
# Check that every product_id in order_items exists in products.csv
#
# Hint:
#   - Get the set of product_ids from products_df
#   - Get the set of product_ids from order_items_df
#   - Find product_ids in order_items that do NOT exist in products
#   - Print the count — expected result: 0
#
# YOUR CODE BELOW:
missing_in_product = ~order_items_df["product_id"].isin(products_df["product_id"])
# 2. Count how many are missing and print the result (Expected result: 0)
print(f"Missing Products Count: {missing_in_product.sum()}")

# ══════════════════════════════════════════════════════════════
# SECTION 5 — FINANCIAL CONSISTENCY
# ══════════════════════════════════════════════════════════════

print("\n── Section 5: Financial Consistency ─────────────────────")

# ✅ PROVIDED — Check that total_price = quantity × unit_price in order_items
order_items_df["calculated_price"] = (
    order_items_df["quantity"] * order_items_df["unit_price"]
).round(2)

price_mismatch = (
    order_items_df["total_price"] != order_items_df["calculated_price"]
).sum()

print(f"total_price mismatches    : {price_mismatch}")

# 🔨 TASK 5A ───────────────────────────────────────────────────
# Check that orders.total_amount equals the sum of order_items.total_price
# for each order.
#
# Hint:
#   - Group order_items_df by order_id and sum total_price
#   - Merge that result with orders_df on order_id
#   - Compare orders.total_amount vs the summed value
#   - Round both to 2 decimal places before comparing
#   - Print count of mismatches — expected result: 0
#
# YOUR CODE BELOW:
item_totals = (order_items_df.groupby("order_id")["total_price"].sum().reset_index())
merged_df = orders_df.merge(item_totals, on="order_id", how="inner")
mismatches = merged_df["total_amount"].round(2) != merged_df["total_price"].round(2)
mismatch_count = mismatches.sum()
print(f"Count of amount mismatches: {mismatch_count}")

# ══════════════════════════════════════════════════════════════
# SECTION 6 — BUSINESS RULE CHECKS
# ══════════════════════════════════════════════════════════════

print("\n── Section 6: Business Rules ────────────────────────────")

# ✅ PROVIDED — Valid order statuses
valid_statuses    = {"PENDING", "CONFIRMED", "SHIPPED", "DELIVERED", "CANCELLED"}
invalid_statuses  = (~orders_df["order_status"].isin(valid_statuses)).sum()
print(f"Invalid order statuses    : {invalid_statuses}")

# ✅ PROVIDED — No zero or negative total_amount
print(f"Zero/negative total_amount: {(orders_df['total_amount'] <= 0).sum()}")

# 🔨 TASK 6A ───────────────────────────────────────────────────
# Check that no order has a negative or zero quantity in order_items.
#
# Hint:
#   - Check order_items_df["quantity"] <= 0
#   - Print the count — expected result: 0
#
# YOUR CODE BELOW:
print(f"Negative Quantity Value Rows: {(order_items_df['quantity'] <= 0).sum()}")

# 🔨 TASK 6B ───────────────────────────────────────────────────
# Check that no order has a negative or zero unit_price in order_items.
#
# Hint:
#   - Check order_items_df["unit_price"] <= 0
#   - Print the count — expected result: 0
#
# YOUR CODE BELOW:
print(f"Negative Unit Price value Rows: {(order_items_df['unit_price'] <= 0).sum()}")

# ══════════════════════════════════════════════════════════════
# SECTION 7 — DUPLICATE PRODUCT PER ORDER
# ══════════════════════════════════════════════════════════════

print("\n── Section 7: Duplicate Product Per Order ───────────────")

# 🔨 TASK 7 ────────────────────────────────────────────────────
# We enforced Option B: each product must appear at most ONCE per order.
# Verify this is true across all orders.
#
# Hint:
#   - Group order_items_df by ["order_id", "product_id"]
#   - Count occurrences
#   - Any count > 1 means the same product appears twice in the same order
#   - Print the count of violations — expected result: 0
#
# YOUR CODE BELOW:
duplicate_rows = order_items_df.duplicated(subset=["order_id", "product_id"])

print(f"Count of duplicate product violations: {duplicate_rows.sum()}")


# ══════════════════════════════════════════════════════════════
# SECTION 8 — TIMESTAMP VALIDITY  (provided for you as example)
# ══════════════════════════════════════════════════════════════

print("\n── Section 8: Timestamps ────────────────────────────────")

print(
    f"Orders updated_at < created_at     : "
    f"{(orders_df['updated_at'] < orders_df['created_at']).sum()}"
)
print(
    f"Order items updated_at < created_at: "
    f"{(order_items_df['updated_at'] < order_items_df['created_at']).sum()}"
)

# ══════════════════════════════════════════════════════════════
# SECTION 9 — DISTRIBUTION SUMMARY  (provided for you as example)
# ══════════════════════════════════════════════════════════════

print("\n── Section 9: Distributions ─────────────────────────────")

print("\nOrder status distribution:")
print(orders_df["order_status"].value_counts())

print("\nItems per order distribution:")
print(
    order_items_df.groupby("order_id")
    .size()
    .value_counts()
    .sort_index()
    .rename("order_count")
)