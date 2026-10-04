# src/retailpulse/silver/silver_verification.py

import pandas as pd
from retailpulse.db_connection import get_db_connection

conn = get_db_connection()

print("=" * 65)
print("  SILVER VERIFICATION")
print("=" * 65)

# ══════════════════════════════════════════════════════════════
# SECTION 1 — ROW COUNTS  (provided)
# ══════════════════════════════════════════════════════════════

print("\n── Section 1: Row Counts ────────────────────────────────")

tables = [
    "customers", "products", "orders", "order_items",
    "payments", "shipments", "campaigns", "campaign_customers"
]

for table in tables:
    with conn.cursor() as cur:
        cur.execute(f"SELECT COUNT(*) FROM silver.{table};")
        count = cur.fetchone()[0]
    print(f"   silver.{table:<25} : {count:>8,}")

# ══════════════════════════════════════════════════════════════
# SECTION 2 — REJECTED RECORDS  (provided)
# ══════════════════════════════════════════════════════════════

print("\n── Section 2: Rejected Records ──────────────────────────")

with conn.cursor() as cur:
    cur.execute("""
        SELECT source_table, COUNT(*) as rejected_count
        FROM silver.rejected_records
        GROUP BY source_table
        ORDER BY source_table;
    """)
    results = cur.fetchall()

total_rejected = 0
for source_table, count in results:
    print(f"   {source_table:<30} : {count:>6,} rejected")
    total_rejected += count

print(f"\n   Total rejected : {total_rejected:,}")

# ══════════════════════════════════════════════════════════════
# SECTION 3 — DATA TYPE VERIFICATION  (provided)
# ══════════════════════════════════════════════════════════════

print("\n── Section 3: Data Types ────────────────────────────────")

with conn.cursor() as cur:
    cur.execute("""
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_schema = 'silver'
        AND   table_name   = 'orders'
        ORDER BY ordinal_position;
    """)
    cols = cur.fetchall()

for col_name, data_type in cols:
    print(f"   {col_name:<25} : {data_type}")

# ══════════════════════════════════════════════════════════════
# SECTION 4 — NULL CHECKS ON CRITICAL COLUMNS
# ══════════════════════════════════════════════════════════════

print("\n── Section 4: Critical NULL Checks ─────────────────────")

# ✅ PROVIDED
with conn.cursor() as cur:
    cur.execute("SELECT COUNT(*) FROM silver.orders WHERE order_id IS NULL;")
    print(f"   NULL order_id in silver.orders     : {cur.fetchone()[0]}")

with conn.cursor() as cur:
    cur.execute("SELECT COUNT(*) FROM silver.orders WHERE customer_id IS NULL;")
    print(f"   NULL customer_id in silver.orders  : {cur.fetchone()[0]}")

# 🔨 TASK 4A ───────────────────────────────────────────────────
# Check that no silver.products row has a NULL product_id
# Check that no silver.products row has a NULL unit_price
#
# Expected: 0 for both
#
# YOUR CODE BELOW:


# 🔨 TASK 4B ───────────────────────────────────────────────────
# Check that no silver.payments row has a NULL payment_id
# Check that no silver.payments row has a NULL order_id
#
# Expected: 0 for both
#
# YOUR CODE BELOW:


# ══════════════════════════════════════════════════════════════
# SECTION 5 — BUSINESS RULE VALIDATION
# ══════════════════════════════════════════════════════════════

print("\n── Section 5: Business Rules ────────────────────────────")

# ✅ PROVIDED — No invalid order statuses in Silver
with conn.cursor() as cur:
    cur.execute("""
        SELECT COUNT(*) FROM silver.orders
        WHERE order_status NOT IN
            ('PENDING','CONFIRMED','SHIPPED','DELIVERED','CANCELLED');
    """)
    print(f"   Invalid order statuses   : {cur.fetchone()[0]}")

# 🔨 TASK 5A ───────────────────────────────────────────────────
# Check no invalid payment_status exists in silver.payments
# Valid: COMPLETED, FAILED, REFUNDED, PENDING, CANCELLED
#
# Expected: 0
#
# YOUR CODE BELOW:


# 🔨 TASK 5B ───────────────────────────────────────────────────
# Check no invalid payment_method exists in silver.payments
# Valid: UPI, NET_BANKING, CARD, COD
#
# Expected: 0
#
# YOUR CODE BELOW:


# 🔨 TASK 5C ───────────────────────────────────────────────────
# Check no DELIVERED shipment has a NULL actual_delivery_date
# in silver.shipments
#
# Expected: 0
#
# YOUR CODE BELOW:


# ══════════════════════════════════════════════════════════════
# SECTION 6 — REJECTION REASON ANALYSIS  (provided)
# ══════════════════════════════════════════════════════════════

print("\n── Section 6: Top Rejection Reasons ────────────────────")

with conn.cursor() as cur:
    cur.execute("""
        SELECT rejection_reason, COUNT(*) as cnt
        FROM silver.rejected_records
        GROUP BY rejection_reason
        ORDER BY cnt DESC
        LIMIT 10;
    """)
    reasons = cur.fetchall()

for reason, count in reasons:
    print(f"   {count:>6,}  {reason}")

# ══════════════════════════════════════════════════════════════
# SECTION 7 — AUDIT COLUMNS  (provided)
# ══════════════════════════════════════════════════════════════

print("\n── Section 7: Audit Columns ─────────────────────────────")

with conn.cursor() as cur:
    cur.execute("""
        SELECT
            COUNT(*) FILTER (WHERE silver_processed_at IS NULL) as null_processed,
            COUNT(*) FILTER (WHERE ingestion_id IS NULL)        as null_ingestion,
            COUNT(*) FILTER (WHERE source_table IS NULL)        as null_source
        FROM silver.orders;
    """)
    result = cur.fetchone()

print(f"   NULL silver_processed_at : {result[0]}")
print(f"   NULL ingestion_id        : {result[1]}")
print(f"   NULL source_table        : {result[2]}")

# 🔨 TASK 7A ───────────────────────────────────────────────────
# Sample 3 rows from silver.orders and print them.
# Visually confirm:
#   - Proper types (numbers not strings)
#   - Audit columns present
#   - Clean data only
#
# YOUR CODE BELOW:


conn.close()
print("\n✅ Silver verification complete.")