# src/retailpulse/ingestion/bronze_verification.py

import pandas as pd
from pathlib import Path
from retailpulse.db_connection import get_db_connection
from retailpulse.ingestion.bronze_config import SOURCE_FILE_MAP

PROJECT_ROOT = Path(__file__).resolve().parents[3]
SOURCE_DIR   = PROJECT_ROOT / "data" / "source"

conn = get_db_connection()

print("=" * 65)
print("  BRONZE VERIFICATION")
print("=" * 65)

# ══════════════════════════════════════════════════════════════
# SECTION 1 — ROW COUNTS  (provided)
# Compare Bronze PostgreSQL rows vs source dirty CSV rows
# ══════════════════════════════════════════════════════════════

print("\n── Section 1: Row Counts ────────────────────────────────")

checks = [
    ("customers",          "customers",  "customers_dirty.csv"),
    ("products",           "products",   "products_dirty.csv"),
    ("orders",             "orders",     "orders_dirty.csv"),
    ("order_items",        "orders",     "order_items_dirty.csv"),
    ("payments",           "payments",   "payments_dirty.csv"),
    ("shipments",          "shipments",  "shipments_dirty.csv"),
    ("campaigns",          "marketing",  "campaigns_dirty.csv"),
    ("campaign_customers", "marketing",  "campaign_customers_dirty.csv"),
]

for table, folder, filename in checks:
    with conn.cursor() as cur:
        cur.execute(f"SELECT COUNT(*) FROM bronze.{table};")
        db_count = cur.fetchone()[0]

    csv_count = len(pd.read_csv(SOURCE_DIR / folder / filename, dtype=str))

    match = "✅" if db_count == csv_count else "❌"
    print(f"  {match} bronze.{table:<25} DB: {db_count:>8,}  CSV: {csv_count:>8,}")

# ══════════════════════════════════════════════════════════════
# SECTION 2 — AUDIT COLUMNS  (provided)
# Verify audit columns exist and are populated
# ══════════════════════════════════════════════════════════════

print("\n── Section 2: Audit Columns ─────────────────────────────")

with conn.cursor() as cur:
    cur.execute("""
        SELECT
            COUNT(*)                                    AS total_rows,
            COUNT(DISTINCT ingestion_id)                AS distinct_runs,
            COUNT(DISTINCT source_file)                 AS distinct_files,
            COUNT(*) FILTER (WHERE ingested_at IS NULL) AS null_ingested_at,
            COUNT(*) FILTER (WHERE source_file  IS NULL) AS null_source_file,
            COUNT(*) FILTER (WHERE ingestion_id IS NULL) AS null_ingestion_id
        FROM bronze.orders;
    """)
    result = cur.fetchone()

print(f"  Total rows        : {result[0]:,}")
print(f"  Distinct runs     : {result[1]}")
print(f"  Distinct files    : {result[2]}")
print(f"  NULL ingested_at  : {result[3]}")
print(f"  NULL source_file  : {result[4]}")
print(f"  NULL ingestion_id : {result[5]}")

# ══════════════════════════════════════════════════════════════
# SECTION 3 — IDEMPOTENCY CHECK
# ══════════════════════════════════════════════════════════════

print("\n── Section 3: Idempotency ───────────────────────────────")

# 🔨 TASK 3A ───────────────────────────────────────────────────
# Verify the pipeline ran exactly once (one distinct ingestion_id).
# If you ran ingest_bronze.py twice, there should still be
# only ONE distinct ingestion_id per table proving idempotency.
#
# Hint:
#   - Query bronze.orders for COUNT(DISTINCT ingestion_id)
#   - Expected result: 1
#
# YOUR CODE BELOW:
with conn.cursor() as cur:
    for table in SOURCE_FILE_MAP.keys():
        cur.execute(
            f"SELECT COUNT(DISTINCT ingestion_id) FROM bronze.{table};"
        )
        count = cur.fetchone()[0]
        status = "✅ PASS" if count == 1 else f"❌ FAIL ({count})"
        print(f"bronze.{table:<25} : {status}")

# ══════════════════════════════════════════════════════════════
# SECTION 4 — DATA PRESERVED AS-IS
# ══════════════════════════════════════════════════════════════

print("\n── Section 4: Data Preserved As-Is ─────────────────────")

# ✅ PROVIDED — NULLs from source must still be NULL in Bronze
with conn.cursor() as cur:
    cur.execute("""
        SELECT COUNT(*)
        FROM bronze.customers
        WHERE email = 'NaN' 
		OR email IS NULL;
    """)
    null_emails = cur.fetchone()[0]

print(f"  NULL emails in bronze.customers : {null_emails:,}")
print(f"  Expected ~300 from injection    : {'✅' if null_emails >= 200 else '❌'}")

# 🔨 TASK 4A ───────────────────────────────────────────────────
# Verify NULL payment_method rows were preserved in Bronze.
# These were injected at ~1% of 40,200 rows ≈ 400 rows.
#
# Hint:
#   - Query bronze.payments WHERE payment_method IS NULL
#   - Expected: > 0  (NULLs preserved from source)
#
# YOUR CODE BELOW:
print("\n── Section 4A: Payment Null Check ─────────────────────")
with conn.cursor() as cur:
    cur.execute("""
        SELECT COUNT(*) FROM bronze.payments 
        WHERE payment_method is NULL 
        OR payment_method = 'NaN';
    """)
    nullPayment = cur.fetchone()
print(f"Null Payments: {nullPayment[0]}")


# 🔨 TASK 4B ───────────────────────────────────────────────────
# Verify that invalid order statuses from injection
# are present in bronze.orders.
# Valid statuses: PENDING, CONFIRMED, SHIPPED, DELIVERED, CANCELLED
#
# Hint:
#   - Query bronze.orders
#   - Count rows where order_status NOT IN valid list
#   - Expected: > 0  (invalid values preserved from source)
#
# YOUR CODE BELOW:
print("\n── Section 4B: Order Status Check ─────────────────────")

query = """
    SELECT COUNT(*) 
    FROM bronze.orders 
    WHERE order_status NOT IN ('PENDING', 'CONFIRMED', 'SHIPPED', 'DELIVERED', 'CANCELLED')
       OR order_status IS NULL;
"""

with conn.cursor() as cur:
    cur.execute(query)
    invalid_status_count = cur.fetchone()[0]

print(f"Invalid / Injected Order Statuses Count: {invalid_status_count}")

# ══════════════════════════════════════════════════════════════
# SECTION 5 — SCHEMA VALIDATION
# ══════════════════════════════════════════════════════════════

print("\n── Section 5: Schema ────────────────────────────────────")

# ✅ PROVIDED — Verify all Bronze tables exist
with conn.cursor() as cur:
    cur.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'bronze'
        ORDER BY table_name;
    """)
    tables = [row[0] for row in cur.fetchall()]

expected_tables = [
    "campaign_customers", "campaigns", "customers",
    "order_items", "orders", "payments",
    "products", "shipments"
]

for t in expected_tables:
    exists = "✅" if t in tables else "❌"
    print(f"  {exists} bronze.{t}")

# ══════════════════════════════════════════════════════════════
# SECTION 6 — SAMPLE DATA CHECK
# ══════════════════════════════════════════════════════════════

print("\n── Section 6: Sample Rows ───────────────────────────────")

# 🔨 TASK 6A ───────────────────────────────────────────────────
# Print 3 sample rows from bronze.orders to visually confirm:
#   - All original columns are present
#   - Audit columns (ingested_at, source_file, ingestion_id) are filled
#
# Hint:
#   - Use pd.read_sql() with LIMIT 3
#   - Print the result
#
# YOUR CODE BELOW:
# Section 6A — Sample rows without SQLAlchemy warning
print("\n── Section 6A: Sample Rows from bronze.orders ───────────")

with conn.cursor() as cur:
    cur.execute("SELECT * FROM bronze.orders LIMIT 3;")
    cols = [desc[0] for desc in cur.description]
    rows = cur.fetchall()

sample_df = pd.DataFrame(rows, columns=cols)
print(sample_df.to_string(index=False))

conn.close()
print("\n✅ Bronze verification complete.")