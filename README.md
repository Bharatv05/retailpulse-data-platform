<h1 align="center">RetailPulse Data Platform</h1>

<p align="center">
  An end-to-end Data Engineering project simulating a production-style
  retail e-commerce data platform — built phase by phase.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/PostgreSQL-18-336791?logo=postgresql&logoColor=white" />
  <img src="https://img.shields.io/badge/Pandas-150458?logo=pandas&logoColor=white" />
  <img src="https://img.shields.io/badge/Phase-3%20Complete-27AE60" />
</p>

---

## 🎯 Project Goal

Build a reliable **Single Source of Truth** for a retail business by constructing
an end-to-end data platform that evolves from a local Python + PostgreSQL pipeline
into a production-style architecture covering ingestion, validation,
transformation, and analytics.

The platform is designed to answer real business questions:

- What is the total revenue per day / week / month?
- Which products and categories generate the highest revenue?
- Which marketing campaigns produced the best ROI?
- Which customers are most active — and which never purchased?
- What is the refund and cancellation rate over time?

---

## 🗂️ Project Architecture

### Data Flow
External / Simulated Sources ↓ SOURCE ← Simulated CSV files (data/source/) ↓ RAW ← Data preserved exactly as received ↓ BRONZE ← Ingested into PostgreSQL, metadata added ↓ SILVER ← Cleaned, validated, business rules applied ↓ GOLD ← Aggregated, analytics-ready datasets ↓ Dashboards / BI


### Layer Responsibilities

| Layer | Purpose |
|---|---|
| `source/` | Simulated external system data (generated locally) |
| `raw/` | Exact copy of received data — never modified |
| `bronze/` | Ingested layer with audit metadata |
| `silver/` | Validated and cleaned data |
| `gold/` | Business metrics and aggregations |

---

## 🛠️ Technology Stack

| Tool | Purpose |
|---|---|
| Python 3.10+ | Core processing and pipeline logic |
| PostgreSQL 18 | Relational database and storage |
| Pandas | Data generation and manipulation |
| NumPy | Reproducible random generation |
| SQL | Transformations and querying |
| Git | Version control |

**Future phases will introduce:**
PySpark · Docker · Cloud Storage · Airflow · Streaming

---

## 📦 Dataset Overview

The source layer simulates a fully connected retail business:

| Dataset | File(s) | Rows | Description |
|---|---|---|---|
| Customers | `customers.csv` | 10,000 | Customer master — one row per customer |
| Products | `products.csv` | 1,000 | Product master — one row per product |
| Orders | `orders.csv` | 40,000 | Order headers — one row per order |
| Order Items | `order_items.csv` | ~101,952 | Line items — one row per product per order |
| Payments | `payments.csv` | 40,000 | Payment records — one row per order |
| Shipments | `shipments.csv` | ~34,176 | Shipment records for eligible orders |
| Campaigns | `campaigns.csv` | 50 | Marketing campaign master |
| Campaign Customers | `campaign_customers.csv` | ~126,854 | Bridge table — customer × campaign |


---

## 🏗️ Data Generation Design Principles

The data generator is built to reflect **real business behaviour**, not random values.

**1. Referential Integrity**
Order customer IDs come from the customer master.
Order product IDs come from the product master.
Payments and shipments reference real order IDs.

**2. Business Rules Enforced**
- Category-aware product pricing (Cricket vs Running vs Tennis etc.)
- Discontinued products excluded from new orders
- Payment method determines refund vs cancellation logic
- Shipment records only created for eligible order statuses
- COD payments cannot fail or be retried
- Conversion dates always after targeting dates

**3. Realistic Distributions**
- Order item count: weighted 1–10 (small orders most common)
- Payment methods: UPI 35%, CARD 30%, NET_BANKING 20%, COD 15%
- Order status: DELIVERED 60%, SHIPPED 15%, CONFIRMED 10%, PENDING 8%, CANCELLED 7%

**4. Reproducibility**
Fixed random seed (`RANDOM_SEED = 42`) ensures identical output on every run.

**5. Intentional NULLs vs Accidental NULLs**
`actual_delivery_date` is NULL for IN_TRANSIT and PROCESSING shipments — by design.
`conversion_date` is NULL for non-converted campaign customers — by design.
These are validated explicitly in the verification layer.

---

## 🚀 Setup Instructions

### 1. Prerequisites

Ensure the following are installed:

- Python 3.10+
- PostgreSQL 18
- Git

---

### 2. Clone the Repository

```bash
git clone https://github.com/your-username/retailpulse-data-platform.git
cd retailpulse-data-platform

### 3. Create and Activate Virtual Environment

```bash
# Create
python -m venv .venv

```PowerShell
# Activate — PowerShell
.venv\Scripts\Activate.ps1

### 4. Install Dependencies

```bash
pip install -r requirements.txt

### 5. Configure Environment Variables

Copy the example file and fill in your local PostgreSQL credentials:

```bash

cp .env.example .env

Edit .env:

env

  POSTGRES_HOST=localhost
  POSTGRES_PORT=5432
  POSTGRES_DB=retailpulse
  POSTGRES_USER=your_postgres_user
  POSTGRES_PASSWORD=your_postgres_password

⚠️ Create the database manually before proceeding:
SQL
 CREATE DATABASE retailpulse;

### 6. Validate Database Connection

PowerShell

$env:PYTHONPATH="src"
python -m retailpulse.db_test

Expected output: 
PostgreSQL 18.x on x86_64-windows ... ✅

⚙️ Running the Data Generators

Run each generator in dependency order:

PowerShell

# 1. Customers (no dependencies)
python -m retailpulse.data_generation.customers

# 2. Products (no dependencies)
python -m retailpulse.data_generation.products

# 3. Orders (depends on customers + products)
python -m retailpulse.data_generation.orders

# 4. Payments (depends on orders)
python -m retailpulse.data_generation.payments

# 5. Shipments (depends on orders)
python -m retailpulse.data_generation.shipments

# 6. Marketing (depends on customers)
python -m retailpulse.data_generation.marketing

    ⚠️ Generation order matters. Orders require customers and products to exist first.

✅ Running Verification Scripts

Each dataset has a dedicated verification script:

PowerShell

python -m retailpulse.data_generation.customers_verification
python -m retailpulse.data_generation.products_verification
python -m retailpulse.data_generation.orders_verification
python -m retailpulse.data_generation.payment_verification
python -m retailpulse.data_generation.shipments_verification
python -m retailpulse.data_generation.marketing_verification

All scripts check:

    Row counts
    ID uniqueness
    NULL presence (intentional vs accidental)
    Referential integrity
    Business rule compliance
    Date and timestamp logic
    Statistical distributions

### Phase 3.7  — Quality Injection Successful

📊 Injection Summary — Reviewed
Customers

text

Clean  : 10,000 rows
Dirty  : 10,100 rows  (+100 duplicates)

  NULL emails          : 300  (3.0%) ✅
  Invalid email format : 100  (1.0%) ✅
  Duplicate records    : 100  (1.0%) ✅
  Invalid phone        : 101  (1.0%) ✅ (1 extra due to rounding — normal)
  Timestamp reversal   :  50  (0.5%) ✅

Products

text

Clean  : 1,000 rows
Dirty  : 1,005 rows  (+5 duplicates)

  NULL unit_price          : 10  (1.0%) ✅
  Invalid discount         : 10  (1.0%) ✅
  Invalid category combo   : 10  (1.0%) ✅
  Duplicate records        :  5  (0.5%) ✅
  Invalid status           :  5  (0.5%) ✅

Orders

text

Clean  : 40,000 rows
Dirty  : 40,400 rows  (+400 duplicates)

  NULL customer_id       : 400  (1.0%) ✅
  Duplicate records      : 400  (1.0%) ✅
  Invalid order status   : 404  (1.0%) ✅
  Negative total_amount  : 202  (0.5%) ✅
  Timestamp reversal     : 202  (0.5%) ✅

Order Items

text

Clean  : 101,952 rows
Dirty  : 102,461 rows  (+509 duplicates)

  Invalid product_id     : 1,019  (1.0%) ✅
  Invalid order_id       :   509  (0.5%) ✅
  Zero/negative quantity : 1,019  (1.0%) ✅
  Incorrect total_price  : 1,019  (1.0%) ✅
  Duplicate records      :   509  (0.5%) ✅

Payments

text

Clean  : 40,000 rows
Dirty  : 40,200 rows  (+200 duplicates)

  Invalid order_id       : 200  (0.5%) ✅
  Amount mismatch        : 400  (1.0%) ✅
  Invalid payment status : 400  (1.0%) ✅
  Duplicate records      : 200  (0.5%) ✅
  NULL payment_method    : 402  (1.0%) ✅

Shipments

text

Clean  : 34,176 rows
Dirty  : 34,176 rows  (no duplicates injected — by design)

  Invalid order_id         : 170  (0.5%) ✅
  Invalid date sequence    : 341  (1.0%) ✅
  Invalid shipment status  : 341  (1.0%) ✅
  Missing delivered date   : 238  (1.0% of DELIVERED rows) ✅

Campaigns

text

Clean  : 50 rows
Dirty  : 51 rows  (+1 duplicate)

  Invalid date range  : 1  (1 row — dataset is only 50 rows, rates produce ~1) ✅
  Invalid budget      : 1  ✅
  Invalid status      : 1  ✅
  Duplicate record    : 1  ✅

    Small dataset + small rates = very few affected rows. This is statistically correct. With only 50 campaigns, 1% = 0.5 rows → rounds to 1.

Campaign Customers

text

Clean  : 126,854 rows
Dirty  : 129,391 rows  (+2,537 duplicates)

  Invalid campaign_id          :   634  (0.5%) ✅
  Invalid customer_id          : 1,268  (1.0%) ✅
  Duplicate pairs              : 2,537  (2.0%) ✅
  Invalid conversion_date      :   227  (1.0% of converted rows) ✅
  False converted with date    : 1,066  (1.0% of non-converted rows) ✅

📁 Project Structure

data/source/
├── customers/
│   ├── customers.csv              10,000 rows   ✅ clean
│   └── customers_dirty.csv        10,100 rows   ✅ injected
│
├── products/
│   ├── products.csv                1,000 rows   ✅ clean
│   └── products_dirty.csv          1,005 rows   ✅ injected
│
├── orders/
│   ├── orders.csv                 40,000 rows   ✅ clean
│   ├── orders_dirty.csv           40,400 rows   ✅ injected
│   ├── order_items.csv           101,952 rows   ✅ clean
│   └── order_items_dirty.csv     102,461 rows   ✅ injected
│
├── payments/
│   ├── payments.csv               40,000 rows   ✅ clean
│   └── payments_dirty.csv         40,200 rows   ✅ injected
│
├── shipments/
│   ├── shipments.csv              34,176 rows   ✅ clean
│   └── shipments_dirty.csv        34,176 rows   ✅ injected
│
└── marketing/
    ├── campaigns.csv                  50 rows   ✅ clean
    ├── campaigns_dirty.csv            51 rows   ✅ injected
    ├── campaign_customers.csv    126,854 rows   ✅ clean
    └── campaign_customers_dirty.csv 129,391 rows ✅ injected
    
📋 Phase Progress
Phase	Description	Status
Phase 1	Environment setup, PostgreSQL, virtual environment	✅ Complete
Phase 2	Business requirements and documentation	✅ Complete
Phase 3	Source data generation and validation	✅ Complete
Phase 4	Bronze layer ingestion into PostgreSQL	🔄 Next
Phase 5	Silver layer — validation and cleaning	⏳ Upcoming
Phase 6	Gold layer — business aggregations	⏳ Upcoming
Phase 7	PySpark processing	⏳ Upcoming
Phase 8	Docker containerisation	⏳ Upcoming
Phase 9	Cloud deployment	⏳ Upcoming
Phase 10	Streaming and real-time processing	⏳ Upcoming

