# src/retailpulse/ingestion/bronze_config.py

"""
Bronze table definitions.

Design rules:
  - Every source column stored as TEXT
  - No foreign key constraints
  - No NOT NULL constraints on source columns
  - No UNIQUE constraints — Bronze accepts everything including duplicates
  - Three audit columns added to every table
  - Idempotency handled by source_file check in ingest_bronze.py
"""

BRONZE_SCHEMA = "bronze"

CREATE_SCHEMA = f"CREATE SCHEMA IF NOT EXISTS {BRONZE_SCHEMA};"

AUDIT_COLUMNS = """
    ingested_at   TIMESTAMP NOT NULL DEFAULT NOW(),
    source_file   TEXT      NOT NULL,
    ingestion_id  TEXT      NOT NULL
"""

CREATE_CUSTOMERS = f"""
CREATE TABLE IF NOT EXISTS {BRONZE_SCHEMA}.customers (
    customer_id      TEXT,
    customer_name    TEXT,
    email            TEXT,
    phone            TEXT,
    city             TEXT,
    state            TEXT,
    country          TEXT,
    signup_date      TEXT,
    customer_status  TEXT,
    created_at       TEXT,
    updated_at       TEXT,
    {AUDIT_COLUMNS}
);
"""

CREATE_PRODUCTS = f"""
CREATE TABLE IF NOT EXISTS {BRONZE_SCHEMA}.products (
    product_id           TEXT,
    product_name         TEXT,
    category             TEXT,
    subcategory          TEXT,
    brand                TEXT,
    unit                 TEXT,
    unit_price           TEXT,
    discount_percentage  TEXT,
    product_status       TEXT,
    created_at           TEXT,
    updated_at           TEXT,
    {AUDIT_COLUMNS}
);
"""

CREATE_ORDERS = f"""
CREATE TABLE IF NOT EXISTS {BRONZE_SCHEMA}.orders (
    order_id      TEXT,
    customer_id   TEXT,
    order_date    TEXT,
    order_status  TEXT,
    total_amount  TEXT,
    created_at    TEXT,
    updated_at    TEXT,
    {AUDIT_COLUMNS}
);
"""

CREATE_ORDER_ITEMS = f"""
CREATE TABLE IF NOT EXISTS {BRONZE_SCHEMA}.order_items (
    order_item_id  TEXT,
    order_id       TEXT,
    product_id     TEXT,
    quantity       TEXT,
    unit_price     TEXT,
    total_price    TEXT,
    created_at     TEXT,
    updated_at     TEXT,
    {AUDIT_COLUMNS}
);
"""

CREATE_PAYMENTS = f"""
CREATE TABLE IF NOT EXISTS {BRONZE_SCHEMA}.payments (
    payment_id        TEXT,
    order_id          TEXT,
    payment_method    TEXT,
    payment_status    TEXT,
    payment_amount    TEXT,
    payment_date      TEXT,
    payment_retried   TEXT,
    created_at        TEXT,
    updated_at        TEXT,
    {AUDIT_COLUMNS}
);
"""

CREATE_SHIPMENTS = f"""
CREATE TABLE IF NOT EXISTS {BRONZE_SCHEMA}.shipments (
    shipment_id             TEXT,
    order_id                TEXT,
    shipment_status         TEXT,
    carrier                 TEXT,
    shipment_date           TEXT,
    expected_delivery_date  TEXT,
    actual_delivery_date    TEXT,
    created_at              TEXT,
    updated_at              TEXT,
    {AUDIT_COLUMNS}
);
"""

CREATE_CAMPAIGNS = f"""
CREATE TABLE IF NOT EXISTS {BRONZE_SCHEMA}.campaigns (
    campaign_id      TEXT,
    campaign_name    TEXT,
    channel          TEXT,
    start_date       TEXT,
    end_date         TEXT,
    budget           TEXT,
    campaign_status  TEXT,
    created_at       TEXT,
    updated_at       TEXT,
    {AUDIT_COLUMNS}
);
"""

CREATE_CAMPAIGN_CUSTOMERS = f"""
CREATE TABLE IF NOT EXISTS {BRONZE_SCHEMA}.campaign_customers (
    id               TEXT,
    campaign_id      TEXT,
    customer_id      TEXT,
    targeted_date    TEXT,
    converted        TEXT,
    conversion_date  TEXT,
    created_at       TEXT,
    updated_at       TEXT,
    {AUDIT_COLUMNS}
);
"""

ALL_CREATE_STATEMENTS = [
    CREATE_CUSTOMERS,
    CREATE_PRODUCTS,
    CREATE_ORDERS,
    CREATE_ORDER_ITEMS,
    CREATE_PAYMENTS,
    CREATE_SHIPMENTS,
    CREATE_CAMPAIGNS,
    CREATE_CAMPAIGN_CUSTOMERS,
]

SOURCE_FILE_MAP = {
    "customers"          : ("customers",  "customers_dirty.csv"),
    "products"           : ("products",   "products_dirty.csv"),
    "orders"             : ("orders",     "orders_dirty.csv"),
    "order_items"        : ("orders",     "order_items_dirty.csv"),
    "payments"           : ("payments",   "payments_dirty.csv"),
    "shipments"          : ("shipments",  "shipments_dirty.csv"),
    "campaigns"          : ("marketing",  "campaigns_dirty.csv"),
    "campaign_customers" : ("marketing",  "campaign_customers_dirty.csv"),
}