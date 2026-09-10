# src/retailpulse/data_generation/payments_verification.py

import pandas as pd
from pathlib import Path

# ── Load Data ──────────────────────────────────────────────────────────────────

PROJECT_ROOT  = Path(__file__).resolve().parents[3]
SOURCE_DIR    = PROJECT_ROOT / "data" / "source"

payments_df   = pd.read_csv(SOURCE_DIR / "payments" / "payments.csv")
orders_df     = pd.read_csv(SOURCE_DIR / "orders"   / "orders.csv")

payments_df["created_at"]   = pd.to_datetime(payments_df["created_at"])
payments_df["updated_at"]   = pd.to_datetime(payments_df["updated_at"])
payments_df["payment_date"] = pd.to_datetime(payments_df["payment_date"])
orders_df["order_date"]     = pd.to_datetime(orders_df["order_date"])

print("=" * 60)
print("  PAYMENTS VERIFICATION")
print("=" * 60)

# ══════════════════════════════════════════════════════════════
# SECTION 1 — BASIC COUNTS  (provided)
# ══════════════════════════════════════════════════════════════

print("\n── Section 1: Basic Counts ──────────────────────────────")
print(f"Payments row count        : {len(payments_df):,}")
print(f"Orders row count          : {len(orders_df):,}")
print(f"One payment per order     : {len(payments_df) == len(orders_df)}")

# ══════════════════════════════════════════════════════════════
# SECTION 2 — UNIQUENESS  (provided)
# ══════════════════════════════════════════════════════════════

print("\n── Section 2: Uniqueness ────────────────────────────────")
print(f"Unique payment_ids        : {payments_df['payment_id'].is_unique}")
print(f"Duplicate payment_ids     : {payments_df['payment_id'].duplicated().sum()}")
print(f"Unique order_ids          : {payments_df['order_id'].is_unique}")
print(f"Duplicate order_ids       : {payments_df['order_id'].duplicated().sum()}")

# ══════════════════════════════════════════════════════════════
# SECTION 3 — NULL CHECKS  (provided)
# ══════════════════════════════════════════════════════════════

print("\n── Section 3: NULL Checks ───────────────────────────────")
print(payments_df.isnull().sum())

# ══════════════════════════════════════════════════════════════
# SECTION 4 — REFERENTIAL INTEGRITY
# ══════════════════════════════════════════════════════════════

print("\n── Section 4: Referential Integrity ─────────────────────")

# ✅ PROVIDED
valid_order_ids   = set(orders_df["order_id"])
payment_order_ids = set(payments_df["order_id"])
print(f"Order IDs not in master   : {len(payment_order_ids - valid_order_ids)}")

# 🔨 TASK 4A ───────────────────────────────────────────────────
# Check that every order in orders.csv has a payment record.
# No order should be missing a payment.
#
# Hint:
#   - Find order_ids in orders that do NOT appear in payments
#   - Expected result: 0
#
# YOUR CODE BELOW:
missing_order_ids = ~orders_df["order_id"].isin(payments_df["order_id"])
print(f"Missing order Id: {missing_order_ids}")

# ══════════════════════════════════════════════════════════════
# SECTION 5 — PAYMENT AMOUNT CONSISTENCY
# ══════════════════════════════════════════════════════════════

print("\n── Section 5: Amount Consistency ────────────────────────")

# 🔨 TASK 5A ───────────────────────────────────────────────────
# Verify that payment_amount matches orders.total_amount for every order.
#
# Hint:
#   - Merge payments_df with orders_df on order_id
#   - Compare payment_amount vs total_amount
#   - Round both to 2 decimal places
#   - Expected mismatches: 0
#
# YOUR CODE BELOW:
merged_df = payments_df.merge(
    orders_df[["order_id", "total_amount"]], on="order_id", how="inner"
)
amount_difference = merged_df["payment_amount"].round(2) != merged_df["total_amount"].round(2)
mismatch_count = amount_difference.sum()
print(f"Count of amount mismatches: {mismatch_count}")

# ══════════════════════════════════════════════════════════════
# SECTION 6 — BUSINESS RULE CHECKS
# ══════════════════════════════════════════════════════════════

print("\n── Section 6: Business Rules ────────────────────────────")

# ✅ PROVIDED — Valid statuses
valid_statuses = {"COMPLETED", "FAILED", "REFUNDED", "PENDING", "CANCELLED"}
print(f"Invalid payment statuses  : {(~payments_df['payment_status'].isin(valid_statuses)).sum()}")

# ✅ PROVIDED — Valid methods
valid_methods  = {"UPI", "NET_BANKING", "CARD", "COD"}
print(f"Invalid payment methods   : {(~payments_df['payment_method'].isin(valid_methods)).sum()}")

# 🔨 TASK 6A ───────────────────────────────────────────────────
# COD payments must NEVER have payment_retried = True.
# Cash cannot fail an online retry.
#
# Hint:
#   - Filter rows where payment_method == "COD"
#   - Check if any of those have payment_retried == True
#   - Expected result: 0
#
# YOUR CODE BELOW:
# 1. Filter rows where payment_method is COD AND payment_retried is True
cod_retried_violations = payments_df[
    (payments_df["payment_method"] == "COD")
    & (payments_df["payment_retried"] == True)
]

print(f"COD with Retried Count: {len(cod_retried_violations)}")

# 🔨 TASK 6B ───────────────────────────────────────────────────
# Cancelled orders paid by UPI, NET_BANKING, or CARD
# must have payment_status = REFUNDED.
#
# Hint:
#   - Merge payments_df with orders_df on order_id
#   - Filter where order_status == CANCELLED
#   - Filter where payment_method != COD
#   - Check if any payment_status != REFUNDED
#   - Expected result: 0
#
# YOUR CODE BELOW:
# order_status_df = orders_df.groupby("order_id")["order_status"]
merged_df = payments_df.merge(
    orders_df[["order_id", "order_status"]], on="order_id", how="inner"
)

# Count directly with .sum()
violation_count = (
    (merged_df["order_status"] == "CANCELLED")
    & (merged_df["payment_method"] != "COD")
    & (merged_df["payment_status"] != "REFUNDED")
).sum()

print(f"Cancelled Via Online Not refunded: {violation_count}")


# 🔨 TASK 6C ───────────────────────────────────────────────────
# Cancelled orders paid by COD must have payment_status = CANCELLED.
# (No money was collected, so no refund — just cancellation.)
#
# Hint:
#   - Merge payments_df with orders_df on order_id
#   - Filter where order_status == CANCELLED AND payment_method == COD
#   - Check if any payment_status != CANCELLED
#   - Expected result: 0
#
# YOUR CODE BELOW:
# 1. Merge payments_df with order_status from orders_df
merged_df = payments_df.merge(
    orders_df[["order_id", "order_status"]], on="order_id", how="inner"
)

# 2. Filter: Cancelled orders AND COD AND payment_status is NOT 'CANCELLED'
violations = merged_df[
    (merged_df["order_status"] == "CANCELLED")
    & (merged_df["payment_method"] == "COD")
    & (merged_df["payment_status"] != "CANCELLED")
]

# 3. Print the count of violations (Expected result: 0)
print(f"Cancelled On COD without Cancelled status: {len(violations)}")

# ══════════════════════════════════════════════════════════════
# SECTION 7 — TIMESTAMP VALIDITY  (provided)
# ══════════════════════════════════════════════════════════════

print("\n── Section 7: Timestamps ────────────────────────────────")
print(f"updated_at < created_at   : {(payments_df['updated_at'] < payments_df['created_at']).sum()}")

# 🔨 TASK 7A ───────────────────────────────────────────────────
# payment_date must always be >= order_date.
# A payment cannot happen before the order was placed.
#
# Hint:
#   - Merge payments_df with orders_df on order_id
#   - Compare payment_date vs order_date
#   - Expected result: 0
#
# YOUR CODE BELOW:
# 1. Merge (to keep the cell self-contained)
merged_df = payments_df.merge(
    orders_df[["order_id", "order_date"]], on="order_id", how="inner"
)

# 2. Convert to datetime
merged_df["payment_date"] = pd.to_datetime(merged_df["payment_date"])
merged_df["order_date"] = pd.to_datetime(merged_df["order_date"])

# 3. Filter for violations (payment before order)
invalid_df = merged_df[merged_df["payment_date"] < merged_df["order_date"]]

# 4. Print count (Expected: 0)
print(f"Date Wrongly Generated: {len(invalid_df)}")

# ══════════════════════════════════════════════════════════════
# SECTION 8 — DISTRIBUTION SUMMARY  (provided)
# ══════════════════════════════════════════════════════════════

print("\n── Section 8: Distributions ─────────────────────────────")

print("\nPayment method distribution:")
print(payments_df["payment_method"].value_counts())

print("\nPayment status distribution:")
print(payments_df["payment_status"].value_counts())

print("\nRetried payments:")
print(payments_df["payment_retried"].value_counts())