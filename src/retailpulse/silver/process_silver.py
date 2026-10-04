# src/retailpulse/silver/process_silver.py

"""
Silver layer processing pipeline.

Processing order per dataset:
  Step 1 → Type cast      (TEXT → proper types, reject uncasting rows)
  Step 2 → NULL check     (reject rows missing critical columns)
  Step 3 → Deduplication  (keep latest updated_at per natural key)
  Step 4 → Business rules (domain values, date logic)
  Step 5 → Route          (valid → silver table, invalid → rejected_records)
"""

import json
from datetime import datetime
from typing   import Tuple

import pandas as pd

from retailpulse.db_connection         import get_db_connection
from retailpulse.silver.silver_config  import (
    SILVER_SCHEMA,
    VALID_CAMPAIGN_CHANNELS,
    VALID_CAMPAIGN_STATUSES,
    VALID_ORDER_STATUSES,
    VALID_PAYMENT_METHODS,
    VALID_PAYMENT_STATUSES,
    VALID_PRODUCT_STATUSES,
    VALID_SHIPMENT_STATUSES,
)
from retailpulse.silver.silver_validators import (
    cast_boolean,
    cast_date,
    cast_integer,
    cast_numeric,
    cast_text,
    cast_timestamp,
    check_domain,
    check_not_null,
    serialise_record,
)

BRONZE_SCHEMA = "bronze"

# ── Quarantine Writer ──────────────────────────────────────────────────────────

def quarantine(
    conn            : object,
    source_table    : str,
    record_id       : str,
    rejection_reason: str,
    raw_record      : dict,
    ingestion_id    : str,
) -> None:
    """Write a rejected record to silver.rejected_records."""
    sql = f"""
        INSERT INTO {SILVER_SCHEMA}.rejected_records
            (source_table, record_id, rejection_reason, raw_record, ingestion_id)
        VALUES (%s, %s, %s, %s, %s);
    """
    with conn.cursor() as cur:
        cur.execute(sql, (
            source_table,
            record_id,
            rejection_reason,
            serialise_record(raw_record),
            ingestion_id,
        ))


# ── Generic Silver Insert ──────────────────────────────────────────────────────

def insert_silver(
    conn         : object,
    table_name   : str,
    row          : dict,
    ingestion_id : str,
    source_table : str,
) -> None:
    """Insert one clean row into the Silver table."""
    row["silver_processed_at"] = datetime.now()
    row["ingestion_id"]        = ingestion_id
    row["source_table"]        = source_table

    columns      = list(row.keys())
    col_names    = ", ".join(columns)
    placeholders = ", ".join(["%s"] * len(columns))

    sql = f"""
        INSERT INTO {SILVER_SCHEMA}.{table_name} ({col_names})
        VALUES ({placeholders})
        ON CONFLICT DO NOTHING;
    """
    with conn.cursor() as cur:
        cur.execute(sql, list(row.values()))


# ── Load From Bronze ───────────────────────────────────────────────────────────

def load_bronze(conn, table_name: str) -> pd.DataFrame:
    """Load all rows from a Bronze table into a DataFrame."""
    with conn.cursor() as cur:
        cur.execute(f"SELECT * FROM {BRONZE_SCHEMA}.{table_name};")
        cols = [desc[0] for desc in cur.description]
        rows = cur.fetchall()
    return pd.DataFrame(rows, columns=cols)


# ── Deduplication ──────────────────────────────────────────────────────────────

def deduplicate(df: pd.DataFrame, key: str) -> pd.DataFrame:
    """
    Keep one row per natural key.
    Priority: most recent updated_at.
    If updated_at is NULL, fall back to created_at.
    """
    df["_sort_key"] = df["updated_at"].fillna(df["created_at"])
    df = (
        df.sort_values("_sort_key", ascending=False)
          .drop_duplicates(subset=[key], keep="first")
          .drop(columns=["_sort_key"])
          .reset_index(drop=True)
    )
    return df


# ══════════════════════════════════════════════════════════════════════════════
# CUSTOMERS
# ══════════════════════════════════════════════════════════════════════════════

def process_customers(conn, ingestion_id: str) -> dict:
    print("\n── Customers ────────────────────────────────────────────")
    df           = load_bronze(conn, "customers")
    total        = len(df)
    clean_count  = 0
    reject_count = 0

    # Step 3 — Deduplicate first on text (before type cast needs sort)
    # We deduplicate on raw text updated_at here to reduce volume
    df = deduplicate(df, "customer_id")

    for _, row in df.iterrows():
        raw = row.to_dict()
        errors = []

        # ── Step 1: Type cast ──────────────────────────────────────────────────
        customer_id,     e = cast_text(row["customer_id"]);      errors += [e] if e else []
        customer_name,   e = cast_text(row["customer_name"]);    errors += [e] if e else []
        email,           e = cast_text(row["email"])
        phone,           e = cast_text(row["phone"])
        city,            e = cast_text(row["city"])
        state,           e = cast_text(row["state"])
        country,         e = cast_text(row["country"])
        signup_date,     e = cast_date(row["signup_date"]);      errors += [e] if e else []
        customer_status, e = cast_text(row["customer_status"])
        created_at,      e = cast_timestamp(row["created_at"]);  errors += [e] if e else []
        updated_at,      e = cast_timestamp(row["updated_at"]);  errors += [e] if e else []

        # ── Step 2: NULL checks on critical columns ────────────────────────────
        e = check_not_null(customer_id, "customer_id");    errors += [e] if e else []
        e = check_not_null(customer_name, "customer_name"); errors += [e] if e else []

        # ── Step 4: Business rules ─────────────────────────────────────────────
        if updated_at and created_at and updated_at < created_at:
            errors.append("updated_at is before created_at")

        # ── Step 5: Route ──────────────────────────────────────────────────────
        if errors:
            quarantine(conn, "customers", customer_id,
                      " | ".join(errors), raw, ingestion_id)
            reject_count += 1
        else:
            insert_silver(conn, "customers", {
                "customer_id"    : customer_id,
                "customer_name"  : customer_name,
                "email"          : email,
                "phone"          : phone,
                "city"           : city,
                "state"          : state,
                "country"        : country,
                "signup_date"    : signup_date,
                "customer_status": customer_status,
                "created_at"     : created_at,
                "updated_at"     : updated_at,
            }, ingestion_id, "bronze.customers")
            clean_count += 1

    conn.commit()
    print(f"   Total bronze rows : {total:>8,}")
    print(f"   After dedup       : {len(df):>8,}")
    print(f"   Clean → Silver    : {clean_count:>8,}")
    print(f"   Rejected          : {reject_count:>8,}")
    return {"clean": clean_count, "rejected": reject_count}


# ══════════════════════════════════════════════════════════════════════════════
# PRODUCTS
# ══════════════════════════════════════════════════════════════════════════════

def process_products(conn, ingestion_id: str) -> dict:
    print("\n── Products ─────────────────────────────────────────────")
    df           = load_bronze(conn, "products")
    total        = len(df)
    clean_count  = 0
    reject_count = 0

    df = deduplicate(df, "product_id")

    for _, row in df.iterrows():
        raw    = row.to_dict()
        errors = []

        product_id,          e = cast_text(row["product_id"]);           errors += [e] if e else []
        product_name,        e = cast_text(row["product_name"]);         errors += [e] if e else []
        category,            e = cast_text(row["category"])
        subcategory,         e = cast_text(row["subcategory"])
        brand,               e = cast_text(row["brand"])
        unit,                e = cast_text(row["unit"])
        unit_price,          e = cast_numeric(row["unit_price"]);        errors += [e] if e else []
        discount_percentage, e = cast_numeric(row["discount_percentage"])
        product_status,      e = cast_text(row["product_status"])
        created_at,          e = cast_timestamp(row["created_at"])
        updated_at,          e = cast_timestamp(row["updated_at"])

        e = check_not_null(product_id,   "product_id");   errors += [e] if e else []
        e = check_not_null(product_name, "product_name"); errors += [e] if e else []
        e = check_not_null(unit_price,   "unit_price");   errors += [e] if e else []

        if unit_price is not None and unit_price <= 0:
            errors.append(f"unit_price {unit_price} must be positive")

        if discount_percentage is not None:
            if discount_percentage < 0 or discount_percentage > 100:
                errors.append(
                    f"discount_percentage {discount_percentage} out of range 0-100"
                )

        e = check_domain(product_status, VALID_PRODUCT_STATUSES, "product_status")
        errors += [e] if e else []

        if errors:
            quarantine(conn, "products", product_id,
                      " | ".join(errors), raw, ingestion_id)
            reject_count += 1
        else:
            insert_silver(conn, "products", {
                "product_id"          : product_id,
                "product_name"        : product_name,
                "category"            : category,
                "subcategory"         : subcategory,
                "brand"               : brand,
                "unit"                : unit,
                "unit_price"          : unit_price,
                "discount_percentage" : discount_percentage,
                "product_status"      : product_status,
                "created_at"          : created_at,
                "updated_at"          : updated_at,
            }, ingestion_id, "bronze.products")
            clean_count += 1

    conn.commit()
    print(f"   Total bronze rows : {total:>8,}")
    print(f"   After dedup       : {len(df):>8,}")
    print(f"   Clean → Silver    : {clean_count:>8,}")
    print(f"   Rejected          : {reject_count:>8,}")
    return {"clean": clean_count, "rejected": reject_count}


# ══════════════════════════════════════════════════════════════════════════════
# ORDERS
# ══════════════════════════════════════════════════════════════════════════════

def process_orders(conn, ingestion_id: str) -> dict:
    print("\n── Orders ───────────────────────────────────────────────")
    df           = load_bronze(conn, "orders")
    total        = len(df)
    clean_count  = 0
    reject_count = 0

    df = deduplicate(df, "order_id")

    for _, row in df.iterrows():
        raw    = row.to_dict()
        errors = []

        order_id,     e = cast_text(row["order_id"]);          errors += [e] if e else []
        customer_id,  e = cast_text(row["customer_id"]);       errors += [e] if e else []
        order_date,   e = cast_date(row["order_date"]);        errors += [e] if e else []
        order_status, e = cast_text(row["order_status"])
        total_amount, e = cast_numeric(row["total_amount"])
        created_at,   e = cast_timestamp(row["created_at"])
        updated_at,   e = cast_timestamp(row["updated_at"])

        e = check_not_null(order_id,    "order_id");    errors += [e] if e else []
        e = check_not_null(customer_id, "customer_id"); errors += [e] if e else []
        e = check_not_null(order_date,  "order_date");  errors += [e] if e else []

        if total_amount is not None and total_amount <= 0:
            errors.append(f"total_amount {total_amount} must be positive")

        e = check_domain(order_status, VALID_ORDER_STATUSES, "order_status")
        errors += [e] if e else []

        if updated_at and created_at and updated_at < created_at:
            errors.append("updated_at is before created_at")

        if errors:
            quarantine(conn, "orders", order_id,
                      " | ".join(errors), raw, ingestion_id)
            reject_count += 1
        else:
            insert_silver(conn, "orders", {
                "order_id"    : order_id,
                "customer_id" : customer_id,
                "order_date"  : order_date,
                "order_status": order_status,
                "total_amount": total_amount,
                "created_at"  : created_at,
                "updated_at"  : updated_at,
            }, ingestion_id, "bronze.orders")
            clean_count += 1

    conn.commit()
    print(f"   Total bronze rows : {total:>8,}")
    print(f"   After dedup       : {len(df):>8,}")
    print(f"   Clean → Silver    : {clean_count:>8,}")
    print(f"   Rejected          : {reject_count:>8,}")
    return {"clean": clean_count, "rejected": reject_count}


# ══════════════════════════════════════════════════════════════════════════════
# ORDER ITEMS
# ══════════════════════════════════════════════════════════════════════════════

def process_order_items(conn, ingestion_id: str) -> dict:
    print("\n── Order Items ──────────────────────────────────────────")
    df           = load_bronze(conn, "order_items")
    total        = len(df)
    clean_count  = 0
    reject_count = 0

    df = deduplicate(df, "order_item_id")

    for _, row in df.iterrows():
        raw    = row.to_dict()
        errors = []

        order_item_id, e = cast_text(row["order_item_id"]);    errors += [e] if e else []
        order_id,      e = cast_text(row["order_id"]);         errors += [e] if e else []
        product_id,    e = cast_text(row["product_id"]);       errors += [e] if e else []
        quantity,      e = cast_integer(row["quantity"]);      errors += [e] if e else []
        unit_price,    e = cast_numeric(row["unit_price"]);    errors += [e] if e else []
        total_price,   e = cast_numeric(row["total_price"]);   errors += [e] if e else []
        created_at,    e = cast_timestamp(row["created_at"])
        updated_at,    e = cast_timestamp(row["updated_at"])

        e = check_not_null(order_item_id, "order_item_id"); errors += [e] if e else []
        e = check_not_null(order_id,      "order_id");      errors += [e] if e else []
        e = check_not_null(product_id,    "product_id");    errors += [e] if e else []

        if quantity is not None and quantity <= 0:
            errors.append(f"quantity {quantity} must be positive")

        if unit_price is not None and unit_price <= 0:
            errors.append(f"unit_price {unit_price} must be positive")

        if errors:
            quarantine(conn, "order_items", order_item_id,
                      " | ".join(errors), raw, ingestion_id)
            reject_count += 1
        else:
            insert_silver(conn, "order_items", {
                "order_item_id" : order_item_id,
                "order_id"      : order_id,
                "product_id"    : product_id,
                "quantity"      : quantity,
                "unit_price"    : unit_price,
                "total_price"   : total_price,
                "created_at"    : created_at,
                "updated_at"    : updated_at,
            }, ingestion_id, "bronze.order_items")
            clean_count += 1

    conn.commit()
    print(f"   Total bronze rows : {total:>8,}")
    print(f"   After dedup       : {len(df):>8,}")
    print(f"   Clean → Silver    : {clean_count:>8,}")
    print(f"   Rejected          : {reject_count:>8,}")
    return {"clean": clean_count, "rejected": reject_count}


# ══════════════════════════════════════════════════════════════════════════════
# PAYMENTS
# ══════════════════════════════════════════════════════════════════════════════

def process_payments(conn, ingestion_id: str) -> dict:
    print("\n── Payments ─────────────────────────────────────────────")
    df           = load_bronze(conn, "payments")
    total        = len(df)
    clean_count  = 0
    reject_count = 0

    df = deduplicate(df, "payment_id")

    for _, row in df.iterrows():
        raw    = row.to_dict()
        errors = []

        payment_id,     e = cast_text(row["payment_id"]);        errors += [e] if e else []
        order_id,       e = cast_text(row["order_id"]);          errors += [e] if e else []
        payment_method, e = cast_text(row["payment_method"])
        payment_status, e = cast_text(row["payment_status"])
        payment_amount, e = cast_numeric(row["payment_amount"])
        payment_date,   e = cast_date(row["payment_date"])
        payment_retried,e = cast_boolean(row["payment_retried"])
        created_at,     e = cast_timestamp(row["created_at"])
        updated_at,     e = cast_timestamp(row["updated_at"])

        e = check_not_null(payment_id, "payment_id"); errors += [e] if e else []
        e = check_not_null(order_id,   "order_id");   errors += [e] if e else []

        e = check_domain(payment_method, VALID_PAYMENT_METHODS, "payment_method")
        errors += [e] if e else []

        e = check_domain(payment_status, VALID_PAYMENT_STATUSES, "payment_status")
        errors += [e] if e else []

        if errors:
            quarantine(conn, "payments", payment_id,
                      " | ".join(errors), raw, ingestion_id)
            reject_count += 1
        else:
            insert_silver(conn, "payments", {
                "payment_id"     : payment_id,
                "order_id"       : order_id,
                "payment_method" : payment_method,
                "payment_status" : payment_status,
                "payment_amount" : payment_amount,
                "payment_date"   : payment_date,
                "payment_retried": payment_retried,
                "created_at"     : created_at,
                "updated_at"     : updated_at,
            }, ingestion_id, "bronze.payments")
            clean_count += 1

    conn.commit()
    print(f"   Total bronze rows : {total:>8,}")
    print(f"   After dedup       : {len(df):>8,}")
    print(f"   Clean → Silver    : {clean_count:>8,}")
    print(f"   Rejected          : {reject_count:>8,}")
    return {"clean": clean_count, "rejected": reject_count}


# ══════════════════════════════════════════════════════════════════════════════
# SHIPMENTS
# ══════════════════════════════════════════════════════════════════════════════

def process_shipments(conn, ingestion_id: str) -> dict:
    print("\n── Shipments ────────────────────────────────────────────")
    df           = load_bronze(conn, "shipments")
    total        = len(df)
    clean_count  = 0
    reject_count = 0

    df = deduplicate(df, "shipment_id")

    for _, row in df.iterrows():
        raw    = row.to_dict()
        errors = []

        shipment_id,            e = cast_text(row["shipment_id"]);           errors += [e] if e else []
        order_id,               e = cast_text(row["order_id"]);              errors += [e] if e else []
        shipment_status,        e = cast_text(row["shipment_status"])
        carrier,                e = cast_text(row["carrier"])
        shipment_date,          e = cast_date(row["shipment_date"])
        expected_delivery_date, e = cast_date(row["expected_delivery_date"])
        actual_delivery_date,   e = cast_date(row["actual_delivery_date"])
        created_at,             e = cast_timestamp(row["created_at"])
        updated_at,             e = cast_timestamp(row["updated_at"])

        e = check_not_null(shipment_id, "shipment_id"); errors += [e] if e else []
        e = check_not_null(order_id,    "order_id");    errors += [e] if e else []

        e = check_domain(shipment_status, VALID_SHIPMENT_STATUSES, "shipment_status")
        errors += [e] if e else []

        if (shipment_date and expected_delivery_date
                and expected_delivery_date < shipment_date):
            errors.append("expected_delivery_date is before shipment_date")

        if (shipment_status == "DELIVERED"
                and actual_delivery_date is None):
            errors.append("DELIVERED shipment missing actual_delivery_date")

        if errors:
            quarantine(conn, "shipments", shipment_id,
                      " | ".join(errors), raw, ingestion_id)
            reject_count += 1
        else:
            insert_silver(conn, "shipments", {
                "shipment_id"            : shipment_id,
                "order_id"               : order_id,
                "shipment_status"        : shipment_status,
                "carrier"                : carrier,
                "shipment_date"          : shipment_date,
                "expected_delivery_date" : expected_delivery_date,
                "actual_delivery_date"   : actual_delivery_date,
                "created_at"             : created_at,
                "updated_at"             : updated_at,
            }, ingestion_id, "bronze.shipments")
            clean_count += 1

    conn.commit()
    print(f"   Total bronze rows : {total:>8,}")
    print(f"   After dedup       : {len(df):>8,}")
    print(f"   Clean → Silver    : {clean_count:>8,}")
    print(f"   Rejected          : {reject_count:>8,}")
    return {"clean": clean_count, "rejected": reject_count}


# ══════════════════════════════════════════════════════════════════════════════
# CAMPAIGNS
# ══════════════════════════════════════════════════════════════════════════════

def process_campaigns(conn, ingestion_id: str) -> dict:
    print("\n── Campaigns ────────────────────────────────────────────")
    df           = load_bronze(conn, "campaigns")
    total        = len(df)
    clean_count  = 0
    reject_count = 0

    df = deduplicate(df, "campaign_id")

    for _, row in df.iterrows():
        raw    = row.to_dict()
        errors = []

        campaign_id,     e = cast_text(row["campaign_id"]);     errors += [e] if e else []
        campaign_name,   e = cast_text(row["campaign_name"])
        channel,         e = cast_text(row["channel"])
        start_date,      e = cast_date(row["start_date"])
        end_date,        e = cast_date(row["end_date"])
        budget,          e = cast_numeric(row["budget"])
        campaign_status, e = cast_text(row["campaign_status"])
        created_at,      e = cast_timestamp(row["created_at"])
        updated_at,      e = cast_timestamp(row["updated_at"])

        e = check_not_null(campaign_id, "campaign_id"); errors += [e] if e else []

        if budget is not None and budget <= 0:
            errors.append(f"budget {budget} must be positive")

        if start_date and end_date and end_date < start_date:
            errors.append("end_date is before start_date")

        e = check_domain(channel,         VALID_CAMPAIGN_CHANNELS, "channel")
        errors += [e] if e else []
        e = check_domain(campaign_status, VALID_CAMPAIGN_STATUSES, "campaign_status")
        errors += [e] if e else []

        if errors:
            quarantine(conn, "campaigns", campaign_id,
                      " | ".join(errors), raw, ingestion_id)
            reject_count += 1
        else:
            insert_silver(conn, "campaigns", {
                "campaign_id"    : campaign_id,
                "campaign_name"  : campaign_name,
                "channel"        : channel,
                "start_date"     : start_date,
                "end_date"       : end_date,
                "budget"         : budget,
                "campaign_status": campaign_status,
                "created_at"     : created_at,
                "updated_at"     : updated_at,
            }, ingestion_id, "bronze.campaigns")
            clean_count += 1

    conn.commit()
    print(f"   Total bronze rows : {total:>8,}")
    print(f"   After dedup       : {len(df):>8,}")
    print(f"   Clean → Silver    : {clean_count:>8,}")
    print(f"   Rejected          : {reject_count:>8,}")
    return {"clean": clean_count, "rejected": reject_count}


# ══════════════════════════════════════════════════════════════════════════════
# CAMPAIGN CUSTOMERS
# ══════════════════════════════════════════════════════════════════════════════

def process_campaign_customers(conn, ingestion_id: str) -> dict:
    print("\n── Campaign Customers ───────────────────────────────────")
    df           = load_bronze(conn, "campaign_customers")
    total        = len(df)
    clean_count  = 0
    reject_count = 0

    df = deduplicate(df, "id")

    for _, row in df.iterrows():
        raw    = row.to_dict()
        errors = []

        id_,             e = cast_text(row["id"]);              errors += [e] if e else []
        campaign_id,     e = cast_text(row["campaign_id"]);     errors += [e] if e else []
        customer_id,     e = cast_text(row["customer_id"]);     errors += [e] if e else []
        targeted_date,   e = cast_date(row["targeted_date"])
        converted,       e = cast_boolean(row["converted"])
        conversion_date, e = cast_date(row["conversion_date"])
        created_at,      e = cast_timestamp(row["created_at"])
        updated_at,      e = cast_timestamp(row["updated_at"])

        e = check_not_null(id_,         "id");          errors += [e] if e else []
        e = check_not_null(campaign_id, "campaign_id"); errors += [e] if e else []
        e = check_not_null(customer_id, "customer_id"); errors += [e] if e else []

        if converted is False and conversion_date is not None:
            errors.append("converted=False but conversion_date is set")

        if converted is True and conversion_date is None:
            errors.append("converted=True but conversion_date is missing")

        if (targeted_date and conversion_date
                and conversion_date < targeted_date):
            errors.append("conversion_date is before targeted_date")

        if errors:
            quarantine(conn, "campaign_customers", id_,
                      " | ".join(errors), raw, ingestion_id)
            reject_count += 1
        else:
            insert_silver(conn, "campaign_customers", {
                "id"             : id_,
                "campaign_id"    : campaign_id,
                "customer_id"    : customer_id,
                "targeted_date"  : targeted_date,
                "converted"      : converted,
                "conversion_date": conversion_date,
                "created_at"     : created_at,
                "updated_at"     : updated_at,
            }, ingestion_id, "bronze.campaign_customers")
            clean_count += 1

    conn.commit()
    print(f"   Total bronze rows : {total:>8,}")
    print(f"   After dedup       : {len(df):>8,}")
    print(f"   Clean → Silver    : {clean_count:>8,}")
    print(f"   Rejected          : {reject_count:>8,}")
    return {"clean": clean_count, "rejected": reject_count}


# ══════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":

    ingestion_id = f"SILVER_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    print("=" * 65)
    print("  SILVER PROCESSING")
    print(f"  ingestion_id : {ingestion_id}")
    print("=" * 65)

    conn = get_db_connection()

    summary = {}

    try:
        summary["customers"]         = process_customers(conn, ingestion_id)
        summary["products"]          = process_products(conn, ingestion_id)
        summary["orders"]            = process_orders(conn, ingestion_id)
        summary["order_items"]       = process_order_items(conn, ingestion_id)
        summary["payments"]          = process_payments(conn, ingestion_id)
        summary["shipments"]         = process_shipments(conn, ingestion_id)
        summary["campaigns"]         = process_campaigns(conn, ingestion_id)
        summary["campaign_customers"]= process_campaign_customers(conn, ingestion_id)
    finally:
        conn.close()

    print("\n" + "=" * 65)
    print("  SILVER PROCESSING SUMMARY")
    print("=" * 65)
    print(f"  {'Dataset':<25} {'Clean':>8}  {'Rejected':>8}")
    print(f"  {'-'*25} {'-'*8}  {'-'*8}")
    for table, counts in summary.items():
        print(f"  {table:<25} {counts['clean']:>8,}  {counts['rejected']:>8,}")