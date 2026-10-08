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
print("\n── Section 4A: Critical NULL Checks ─────────────────────")

with conn.cursor() as cur:
    cur.execute("SELECT COUNT(*) from silver.products where product_id IS NULL;")
    print(f"    Null product_id in silver.products    :{cur.fetchone()[0]}")

with conn.cursor() as cur:
    cur.execute("SELECT COUNT(*) from silver.products WHERE unit_price IS NULL;")
    print(f"    NULL unit_price in silver.products     :{cur.fetchone()[0]}")
# 🔨 TASK 4B ───────────────────────────────────────────────────
# Check that no silver.payments row has a NULL payment_id
# Check that no silver.payments row has a NULL order_id
#
# Expected: 0 for both
#
# YOUR CODE BELOW:
print("\n── Section 4B: Critical NULL Checks ─────────────────────")

with conn.cursor() as cur:
    cur.execute("""SELECT 
                   COUNT(*) FILTER (WHERE payment_id IS NULL) as null_product_id,
                   COUNT(*) FILTER (WHERE order_id IS NULL) as null_order_id
                   FROM silver.payments
                """)
    null_pid, null_oid = cur.fetchone()
print(f"    NULL payment_id in silver.payments     :{null_pid}")
print(f"    NULL order_id in silver.payments       :{null_oid}")

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

payment_sts_query = """
                        SELECT COUNT(*) FROM silver.payments
                        WHERE payment_status 
                        NOT IN ('COMPLETED', 'FAILED', 'REFUNDED', 'PENDING', 'CANCELLED')
                    """
with conn.cursor() as cur:
    cur.execute(payment_sts_query)
    print(f"   Invalid payment statuses   : {cur.fetchone()[0]}")


# 🔨 TASK 5B ───────────────────────────────────────────────────
# Check no invalid payment_method exists in silver.payments
# Valid: UPI, NET_BANKING, CARD, COD
#
# Expected: 0
#
# YOUR CODE BELOW:
payment_method_query = """
                            SELECT 
                                COUNT(*)
                            FROM 
                                silver.payments
                            WHERE 
                                payment_method NOT IN ('UPI', 'NET_BANKING', 'CARD', 'COD');
                        """

with conn.cursor() as cur:
    cur.execute(payment_method_query)
    print(f"   Invalid payment method statuses   : {cur.fetchone()[0]}")

# 🔨 TASK 5C ───────────────────────────────────────────────────
# Check no DELIVERED shipment has a NULL actual_delivery_date
# in silver.shipments
#
# Expected: 0
#
# YOUR CODE BELOW:
with conn.cursor() as cur:
    cur.execute("SELECT COUNT(*) FROM silver.shipments WHERE actual_delivery_date IS NULL AND shipment_status = 'DELIVERED'")
    print(f"   Invalid Delivery Without Date   : {cur.fetchone()[0]}")


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

print("\n── Section 7A: Sample 3 rows from silver.orders ──────────")

# Set display options so all columns are visible in console
pd.set_option("display.max_columns", None)
pd.set_option("display.width", 1000)

sample_orders = pd.read_sql("SELECT * FROM silver.orders LIMIT 3;", conn)

print("TOP 3 DATA FROM ORDERS:")
print(sample_orders.to_string(index=False))

# Optional: Check data types
print("\nColumn Data Types:")
print(sample_orders.dtypes)

print("\n── Section 7A: Sample 3 rows from silver.orders ──────────")

with conn.cursor() as cur:
    cur.execute("SELECT * FROM silver.orders LIMIT 3;")
    rows = cur.fetchall()  # Fetch all 3 rows
    headers = [desc[0] for desc in cur.description]  # Extract column names

# Print Header
print(f"TOP 3 DATA FROM ORDERS:\n{' | '.join(headers)}")
print("-" * 100)

# Print Rows
for row in rows:
    print(" | ".join(str(val) for val in row))

conn.close()
print("\n✅ Silver verification complete.")