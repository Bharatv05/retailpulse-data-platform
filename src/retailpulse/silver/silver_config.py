# src/retailpulse/silver/silver_config.py

"""
Silver layer table definitions.

Design rules:
  - Proper data types enforced (not TEXT like Bronze)
  - One rejected_records table shared across all datasets
  - Three audit columns added to every silver table
  - Idempotency handled by checking source ingestion_id
"""

SILVER_SCHEMA = "silver"

CREATE_SCHEMA = f"CREATE SCHEMA IF NOT EXISTS {SILVER_SCHEMA};"

# ── Audit columns added to every Silver table ──────────────────────────────────

AUDIT_COLUMNS = """
    silver_processed_at  TIMESTAMP  NOT NULL DEFAULT NOW(),
    ingestion_id         TEXT       NOT NULL,
    source_table         TEXT       NOT NULL
"""

# ── Rejected Records Table ─────────────────────────────────────────────────────
# All datasets share one rejected_records table.
# Each row records exactly why a Bronze record was not accepted.

CREATE_REJECTED_RECORDS = f"""
CREATE TABLE IF NOT EXISTS {SILVER_SCHEMA}.rejected_records (
    id               SERIAL PRIMARY KEY,
    source_table     TEXT       NOT NULL,
    record_id        TEXT,
    rejection_reason TEXT       NOT NULL,
    raw_record       TEXT       NOT NULL,
    ingestion_id     TEXT       NOT NULL,
    rejected_at      TIMESTAMP  NOT NULL DEFAULT NOW()
);
"""

# ── Customers ──────────────────────────────────────────────────────────────────

CREATE_CUSTOMERS = f"""
CREATE TABLE IF NOT EXISTS {SILVER_SCHEMA}.customers (
    customer_id      VARCHAR(20)   PRIMARY KEY,
    customer_name    TEXT          NOT NULL,
    email            TEXT,
    phone            TEXT,
    city             TEXT,
    state            TEXT,
    country          TEXT,
    signup_date      DATE,
    customer_status  VARCHAR(20),
    created_at       TIMESTAMP,
    updated_at       TIMESTAMP,
    {AUDIT_COLUMNS}
);
"""

# ── Products ───────────────────────────────────────────────────────────────────

CREATE_PRODUCTS = f"""
CREATE TABLE IF NOT EXISTS {SILVER_SCHEMA}.products (
    product_id           VARCHAR(20)   PRIMARY KEY,
    product_name         TEXT          NOT NULL,
    category             TEXT,
    subcategory          TEXT,
    brand                TEXT,
    unit                 TEXT,
    unit_price           NUMERIC(12,2),
    discount_percentage  NUMERIC(5,2),
    product_status       VARCHAR(20),
    created_at           TIMESTAMP,
    updated_at           TIMESTAMP,
    {AUDIT_COLUMNS}
);
"""

# ── Orders ─────────────────────────────────────────────────────────────────────

CREATE_ORDERS = f"""
CREATE TABLE IF NOT EXISTS {SILVER_SCHEMA}.orders (
    order_id      VARCHAR(20)    PRIMARY KEY,
    customer_id   VARCHAR(20)    NOT NULL,
    order_date    DATE           NOT NULL,
    order_status  VARCHAR(30),
    total_amount  NUMERIC(14,2),
    created_at    TIMESTAMP,
    updated_at    TIMESTAMP,
    {AUDIT_COLUMNS}
);
"""

# ── Order Items ────────────────────────────────────────────────────────────────

CREATE_ORDER_ITEMS = f"""
CREATE TABLE IF NOT EXISTS {SILVER_SCHEMA}.order_items (
    order_item_id  VARCHAR(20)    PRIMARY KEY,
    order_id       VARCHAR(20)    NOT NULL,
    product_id     VARCHAR(20)    NOT NULL,
    quantity       INTEGER,
    unit_price     NUMERIC(12,2),
    total_price    NUMERIC(14,2),
    created_at     TIMESTAMP,
    updated_at     TIMESTAMP,
    {AUDIT_COLUMNS}
);
"""

# ── Payments ───────────────────────────────────────────────────────────────────

CREATE_PAYMENTS = f"""
CREATE TABLE IF NOT EXISTS {SILVER_SCHEMA}.payments (
    payment_id        VARCHAR(20)    PRIMARY KEY,
    order_id          VARCHAR(20)    NOT NULL,
    payment_method    VARCHAR(20),
    payment_status    VARCHAR(20),
    payment_amount    NUMERIC(14,2),
    payment_date      DATE,
    payment_retried   BOOLEAN,
    created_at        TIMESTAMP,
    updated_at        TIMESTAMP,
    {AUDIT_COLUMNS}
);
"""

# ── Shipments ──────────────────────────────────────────────────────────────────

CREATE_SHIPMENTS = f"""
CREATE TABLE IF NOT EXISTS {SILVER_SCHEMA}.shipments (
    shipment_id             VARCHAR(20)  PRIMARY KEY,
    order_id                VARCHAR(20)  NOT NULL,
    shipment_status         VARCHAR(20),
    carrier                 TEXT,
    shipment_date           DATE,
    expected_delivery_date  DATE,
    actual_delivery_date    DATE,
    created_at              TIMESTAMP,
    updated_at              TIMESTAMP,
    {AUDIT_COLUMNS}
);
"""

# ── Campaigns ──────────────────────────────────────────────────────────────────

CREATE_CAMPAIGNS = f"""
CREATE TABLE IF NOT EXISTS {SILVER_SCHEMA}.campaigns (
    campaign_id      VARCHAR(20)    PRIMARY KEY,
    campaign_name    TEXT,
    channel          VARCHAR(30),
    start_date       DATE,
    end_date         DATE,
    budget           NUMERIC(14,2),
    campaign_status  VARCHAR(20),
    created_at       TIMESTAMP,
    updated_at       TIMESTAMP,
    {AUDIT_COLUMNS}
);
"""

# ── Campaign Customers ─────────────────────────────────────────────────────────

CREATE_CAMPAIGN_CUSTOMERS = f"""
CREATE TABLE IF NOT EXISTS {SILVER_SCHEMA}.campaign_customers (
    id               VARCHAR(20)   PRIMARY KEY,
    campaign_id      VARCHAR(20)   NOT NULL,
    customer_id      VARCHAR(20)   NOT NULL,
    targeted_date    DATE,
    converted        BOOLEAN,
    conversion_date  DATE,
    created_at       TIMESTAMP,
    updated_at       TIMESTAMP,
    {AUDIT_COLUMNS}
);
"""

# ── All statements in creation order ──────────────────────────────────────────

ALL_CREATE_STATEMENTS = [
    CREATE_REJECTED_RECORDS,
    CREATE_CUSTOMERS,
    CREATE_PRODUCTS,
    CREATE_ORDERS,
    CREATE_ORDER_ITEMS,
    CREATE_PAYMENTS,
    CREATE_SHIPMENTS,
    CREATE_CAMPAIGNS,
    CREATE_CAMPAIGN_CUSTOMERS,
]

# ── Valid domain values ────────────────────────────────────────────────────────

VALID_ORDER_STATUSES      = {"PENDING", "CONFIRMED", "SHIPPED", "DELIVERED", "CANCELLED"}
VALID_PAYMENT_STATUSES    = {"COMPLETED", "FAILED", "REFUNDED", "PENDING", "CANCELLED"}
VALID_PAYMENT_METHODS     = {"UPI", "NET_BANKING", "CARD", "COD"}
VALID_PRODUCT_STATUSES    = {"ACTIVE", "DISCONTINUED"}
VALID_SHIPMENT_STATUSES   = {"PROCESSING", "IN_TRANSIT", "DELIVERED"}
VALID_CAMPAIGN_STATUSES   = {"ACTIVE", "COMPLETED", "PAUSED"}
VALID_CAMPAIGN_CHANNELS   = {"EMAIL", "SMS", "SOCIAL_MEDIA", "PUSH_NOTIFICATION"}