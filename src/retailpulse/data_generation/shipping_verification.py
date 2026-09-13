# src/retailpulse/data_generation/shipments_verification.py

import pandas as pd
from pathlib import Path

# ── Load Data ──────────────────────────────────────────────────────────────────

PROJECT_ROOT  = Path(__file__).resolve().parents[3]
SOURCE_DIR    = PROJECT_ROOT / "data" / "source"

shipments_df  = pd.read_csv(SOURCE_DIR / "shipments" / "shipments.csv",
                             parse_dates=["shipment_date",
                                          "expected_delivery_date",
                                          "actual_delivery_date"])
orders_df     = pd.read_csv(SOURCE_DIR / "orders" / "orders.csv",
                             parse_dates=["order_date"])

shipments_df["created_at"] = pd.to_datetime(shipments_df["created_at"])
shipments_df["updated_at"] = pd.to_datetime(shipments_df["updated_at"])

print("=" * 60)
print("  SHIPMENTS VERIFICATION")
print("=" * 60)

# ══════════════════════════════════════════════════════════════
# SECTION 1 — BASIC COUNTS  (provided)
# ══════════════════════════════════════════════════════════════

print("\n── Section 1: Basic Counts ──────────────────────────────")

eligible_orders = orders_df[
    orders_df["order_status"].isin(["CONFIRMED", "SHIPPED", "DELIVERED"])
]
print(f"Eligible orders (expected) : {len(eligible_orders):,}")
print(f"Shipment rows generated    : {len(shipments_df):,}")
print(f"Counts match               : {len(eligible_orders) == len(shipments_df)}")

# ══════════════════════════════════════════════════════════════
# SECTION 2 — UNIQUENESS  (provided)
# ══════════════════════════════════════════════════════════════

print("\n── Section 2: Uniqueness ────────────────────────────────")
print(f"Unique shipment_ids        : {shipments_df['shipment_id'].is_unique}")
print(f"Duplicate shipment_ids     : {shipments_df['shipment_id'].duplicated().sum()}")
print(f"Unique order_ids           : {shipments_df['order_id'].is_unique}")
print(f"Duplicate order_ids        : {shipments_df['order_id'].duplicated().sum()}")

# ══════════════════════════════════════════════════════════════
# SECTION 3 — NULL CHECKS  (provided)
# ══════════════════════════════════════════════════════════════

print("\n── Section 3: NULL Checks ───────────────────────────────")
print(shipments_df.isnull().sum())

# ══════════════════════════════════════════════════════════════
# SECTION 4 — REFERENTIAL INTEGRITY
# ══════════════════════════════════════════════════════════════

print("\n── Section 4: Referential Integrity ─────────────────────")

# ✅ PROVIDED — No shipment should reference an unknown order
valid_order_ids    = set(orders_df["order_id"])
shipment_order_ids = set(shipments_df["order_id"])
print(f"Order IDs not in master    : {len(shipment_order_ids - valid_order_ids)}")

# 🔨 TASK 4A ───────────────────────────────────────────────────
# PENDING and CANCELLED orders must NOT have a shipment record.
#
# Hint:
#   - Get order_ids where order_status is PENDING or CANCELLED
#   - Check if any of those order_ids appear in shipments_df
#   - Expected result: 0
#
# YOUR CODE BELOW:
cancelle_pending_orders = orders_df[orders_df["order_status"].isin(["PENDING", "CANCELLED"])]
invalid_shipping = (cancelle_pending_orders['order_id'].isin(shipments_df["order_id"]))
print("Pending / Cancelled with Order: ",invalid_shipping)

# ══════════════════════════════════════════════════════════════
# SECTION 5 — BUSINESS RULE CHECKS
# ══════════════════════════════════════════════════════════════

print("\n── Section 5: Business Rules ────────────────────────────")

# ✅ PROVIDED — Valid shipment statuses
valid_statuses = {"PROCESSING", "IN_TRANSIT", "DELIVERED"}
print(f"Invalid shipment statuses  : "
      f"{(~shipments_df['shipment_status'].isin(valid_statuses)).sum()}")

# ✅ PROVIDED — Valid carriers
valid_carriers = {
    "Delhivery", "BlueDart", "DTDC",
    "FedEx", "Ekart", "XpressBees", "India Post"
}
print(f"Invalid carriers           : "
      f"{(~shipments_df['carrier'].isin(valid_carriers)).sum()}")

# 🔨 TASK 5A ───────────────────────────────────────────────────
# DELIVERED orders must have actual_delivery_date filled (not NULL).
# No delivered shipment should have a missing delivery date.
#
# Hint:
#   - Filter shipments where shipment_status == DELIVERED
#   - Check if any actual_delivery_date is NULL
#   - Expected result: 0
#
# YOUR CODE BELOW:
# 1. Filter where shipment is DELIVERED AND actual_delivery_date is missing (NaN/NaT)
missing_delivery_dates = shipments_df[
    (shipments_df["shipment_status"] == "DELIVERED")
    & (shipments_df["actual_delivery_date"].isna())
]

# 2. Print count of violations (Expected result: 0)
print(f"Delivered without Date: {len(missing_delivery_dates)}")

# 🔨 TASK 5B ───────────────────────────────────────────────────
# IN_TRANSIT and PROCESSING shipments must have
# actual_delivery_date = NULL.
# We do not know the future delivery date yet.
#
# Hint:
#   - Filter shipments where shipment_status is IN_TRANSIT or PROCESSING
#   - Check if any actual_delivery_date is NOT NULL
#   - Expected result: 0
#
# YOUR CODE BELOW:
# Count True values directly with .sum()
violation_count = (
    shipments_df["shipment_status"].isin(["IN_TRANSIT", "PROCESSING"])
    & shipments_df["actual_delivery_date"].notna()
).sum()

print(f"In-progress shipments with delivery date: {violation_count}")



# 🔨 TASK 5C ───────────────────────────────────────────────────
# Shipment status must correctly map from order status.
# Rules:
#   CONFIRMED  → PROCESSING
#   SHIPPED    → IN_TRANSIT
#   DELIVERED  → DELIVERED
#
# Hint:
#   - Merge shipments_df with orders_df on order_id
#   - Apply the mapping and check if shipment_status matches
#   - Expected violations: 0
#
# YOUR CODE BELOW:
# 1. Define the expected mapping dictionary
status_map = {
    "CONFIRMED": "PROCESSING",
    "SHIPPED": "IN_TRANSIT",
    "DELIVERED": "DELIVERED",
}

# 2. Merge shipments and orders
merged_df = shipments_df.merge(
    orders_df[["order_id", "order_status"]], on="order_id", how="inner"
)

# 3. Create expected shipment status by mapping order_status
merged_df["expected_shipment_status"] = merged_df["order_status"].map(
    status_map
)

# 4. Find violations where actual status doesn't match expected status
violations = merged_df["shipment_status"] != merged_df["expected_shipment_status"]

# 5. Print violation count (Expected: 0)
print(f"Mapping Violations: {violations.sum()}")

# ══════════════════════════════════════════════════════════════
# SECTION 6 — DATE LOGIC CHECKS
# ══════════════════════════════════════════════════════════════

print("\n── Section 6: Date Logic ────────────────────────────────")

# 🔨 TASK 6A ───────────────────────────────────────────────────
# shipment_date must always be >= order_date.
# A shipment cannot leave before the order was placed.
#
# Hint:
#   - Merge shipments_df with orders_df on order_id
#   - Compare shipment_date vs order_date
#   - Expected result: 0
#
# YOUR CODE BELOW:
# 1. Merge shipments_df with orders_df on order_id
merged_df = shipments_df.merge(
    orders_df[["order_id", "order_date"]], on="order_id", how="inner"
)

# 2. Convert both date columns to datetime
merged_df["shipment_date"] = pd.to_datetime(merged_df["shipment_date"])
merged_df["order_date"] = pd.to_datetime(merged_df["order_date"])

# 3. Check for violations where shipment happened BEFORE order date (<)
violations = merged_df["shipment_date"] < merged_df["order_date"]

# 4. Print the count of violations (Expected result: 0)
print(f"Shipments before order date: {violations.sum()}")


# 🔨 TASK 6B ───────────────────────────────────────────────────
# expected_delivery_date must always be >= shipment_date.
# Delivery cannot be expected before it ships.
#
# Hint:
#   - Compare directly on shipments_df
#   - Expected result: 0
#
# YOUR CODE BELOW:
# 1. Convert date columns to datetime for accurate comparison
expected_date = pd.to_datetime(shipments_df["expected_delivery_date"])
ship_date = pd.to_datetime(shipments_df["shipment_date"])

# 2. Check for violations where expected delivery is BEFORE shipment date (<)
violations = expected_date < ship_date

# 3. Print the count of violations (Expected result: 0)
print(f"Expected delivery before shipment date: {violations.sum()}")

# 🔨 TASK 6C ───────────────────────────────────────────────────
# For DELIVERED shipments:
# actual_delivery_date must be >= shipment_date.
# A package cannot be delivered before it was shipped.
#
# Hint:
#   - Filter DELIVERED rows only
#   - Compare actual_delivery_date vs shipment_date
#   - Expected result: 0
#
# YOUR CODE BELOW:
# 1. Filter mask for delivered status
is_delivered = shipments_df["shipment_status"] == "DELIVERED"

# 2. Convert and check violation condition directly
delivered_before_ship = (
    pd.to_datetime(shipments_df["actual_delivery_date"])
    < pd.to_datetime(shipments_df["shipment_date"])
)

# 3. Combine conditions and sum (Expected: 0)
violations_count = (is_delivered & delivered_before_ship).sum()
print(f"Delivered before shipment date: {violations_count}")

# ══════════════════════════════════════════════════════════════
# SECTION 7 — TIMESTAMP VALIDITY  (provided)
# ══════════════════════════════════════════════════════════════

print("\n── Section 7: Timestamps ────────────────────────────────")
print(f"updated_at < created_at    : "
      f"{(shipments_df['updated_at'] < shipments_df['created_at']).sum()}")

# ══════════════════════════════════════════════════════════════
# SECTION 8 — DISTRIBUTION SUMMARY  (provided)
# ══════════════════════════════════════════════════════════════

print("\n── Section 8: Distributions ─────────────────────────────")

print("\nShipment status distribution:")
print(shipments_df["shipment_status"].value_counts())

print("\nCarrier distribution:")
print(shipments_df["carrier"].value_counts())

print("\nDelivery window (expected - shipment) in days:")
shipments_df["delivery_window_days"] = (
    shipments_df["expected_delivery_date"] - shipments_df["shipment_date"]
).dt.days
print(shipments_df["delivery_window_days"].value_counts().sort_index())