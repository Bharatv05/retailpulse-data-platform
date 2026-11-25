<h1 align="center">🛒 RetailPulse Data Platform</h1>

<p align="center">
  An end-to-end data engineering project that builds a production-style retail data platform,<br/>
  phase by phase: from synthetic source systems to a Bronze → Silver → Gold analytics layer.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/PostgreSQL-18-4169E1?style=flat-square&logo=postgresql&logoColor=white" />
  <img src="https://img.shields.io/badge/Pandas-150458?style=flat-square&logo=pandas&logoColor=white" />
  <img src="https://img.shields.io/badge/NumPy-013243?style=flat-square&logo=numpy&logoColor=white" />
  <img src="https://img.shields.io/badge/Faker-synthetic%20data-6A5ACD?style=flat-square" />
  <img src="https://img.shields.io/badge/Phase%203-Complete-2EA043?style=flat-square" />
  <img src="https://img.shields.io/badge/Next-Phase%204%20Bronze-D29922?style=flat-square" />
</p>

---

## 📌 Why This Project

Real data platforms don't start with clean data. They start with several source systems that disagree with each other, contain duplicates, NULLs, broken references and impossible timestamps.

RetailPulse simulates that reality for a fictional sports-retail e-commerce company and builds the platform that turns it into a **single source of truth** the business can trust. The goal is to answer questions like:

- What is revenue per day / week / month, and which products and categories drive it?
- Which marketing campaigns and channels deliver the best ROI?
- Which customers are most active, and which never purchased?
- What are the refund, cancellation and delivery-delay rates over time?

---

## 🏗️ Architecture

```text
 ┌──────────────────────┐
 │  Simulated sources   │   customers · products · orders · order_items
 │  (data/source/*.csv) │   payments · shipments · campaigns · campaign_customers
 └──────────┬───────────┘
            │  clean + *_dirty.csv (controlled quality issues)
            ▼
 ┌──────────────────────┐
 │  RAW                 │   exact copy of what was received, never modified
 └──────────┬───────────┘
            ▼
 ┌──────────────────────┐
 │  BRONZE (PostgreSQL) │   ingested as-is + audit metadata (load time, source file, batch id)
 └──────────┬───────────┘
            ▼
 ┌──────────────────────┐
 │  SILVER              │   validated against data contracts, deduplicated, typed;
 │                      │   bad records quarantined, not silently dropped
 └──────────┬───────────┘
            ▼
 ┌──────────────────────┐
 │  GOLD                │   facts, dimensions and business KPIs
 └──────────┬───────────┘
            ▼
      Dashboards / BI
```

---

## ✅ What's Built So Far

### 1. Requirements & data contracts (docs first, code second)
Before writing any pipeline code, the project defines what "correct" means:

| Document | What it covers |
|---|---|
| [`business_requirements.md`](docs/business_requirements.md) | Stakeholders, business questions, functional & non-functional requirements (idempotency, lineage, reproducibility, security) |
| [`data_sources.md`](docs/data_sources.md) | Every source system, its format and expected frequency |
| [`data_contracts.md`](docs/data_contracts.md) | Grain, schema, nullability, uniqueness, referential and business rules per dataset, plus schema-change and duplicate-handling policies |
| [`data_dictionary.md`](docs/data_dictionary.md) | Column-level definitions |

### 2. Synthetic source systems with real business behaviour
A modular generator (`src/retailpulse/data_generation/`) produces ~350K connected rows across 8 datasets:

| Dataset | Rows | Grain |
|---|---:|---|
| Customers | 10,000 | one row per customer |
| Products | 1,000 | one row per product |
| Orders | 40,000 | one row per order |
| Order items | ~101,952 | one row per product per order |
| Payments | 40,000 | one row per order payment |
| Shipments | ~34,176 | one row per shipment (eligible orders only) |
| Campaigns | 50 | one row per marketing campaign |
| Campaign customers | ~126,854 | customer × campaign bridge |

The data follows the rules a real business would:
- **Referential integrity:** orders reference real customers and products; payments and shipments reference real orders.
- **Business rules:** category-aware pricing, discontinued products excluded from new orders, COD payments can't fail or retry, shipments only for eligible order statuses, conversions always after targeting.
- **Realistic distributions:** UPI 35% / Card 30% / Net banking 20% / COD 15%; Delivered 60% / Shipped 15% / Confirmed 10% / Pending 8% / Cancelled 7%; small baskets most common.
- **Intentional vs accidental NULLs:** `actual_delivery_date` is NULL for in-transit shipments *by design*, and that is tested explicitly.
- **Reproducible:** fixed `RANDOM_SEED = 42`, so every run produces identical output.
- **Config-driven:** sizes, catalogs, price ranges and distributions all live in [`config.py`](src/retailpulse/data_generation/config.py).

### 3. Controlled data-quality injection
[`quality_injector.py`](src/retailpulse/data_generation/quality_injector.py) writes a `*_dirty.csv` next to every clean file, using declarative rules from [`injector_config.py`](src/retailpulse/data_generation/injector_config.py). Because the dirty data is generated from known clean data, every Silver-layer check can be **measured against a known answer**.

| Dataset | Injected problems (rate) |
|---|---|
| Customers | NULL email (3%), invalid email format, invalid phone, duplicates (1% each), `updated_at < created_at` (0.5%) |
| Products | NULL price, invalid discount (<0 or >100), wrong category/subcategory pair (1% each), invalid status, duplicates |
| Orders | NULL customer_id, invalid status, duplicates (1% each), negative totals, timestamp reversal (0.5%) |
| Order items | orphan product_id, zero/negative quantity, wrong line total (1% each), orphan order_id, duplicates |
| Payments | amount mismatch, invalid status, NULL method (1% each), orphan order_id, duplicates |
| Shipments | shipped after expected delivery, invalid status, DELIVERED with no delivery date (1% each), orphan order_id |
| Campaigns | end before start, negative budget, invalid status, duplicates |
| Campaign customers | duplicate pairs (2%), orphan IDs, conversion before targeting, "not converted" rows with a conversion date |

The injector uses a different random seed from the generator, so it stays reproducible on its own.

### 4. Verification scripts
Verification scripts for products, orders, payments, shipments and marketing check row counts, ID uniqueness, intentional vs accidental NULLs, referential integrity, business-rule compliance, date logic and value distributions.

---

## 🗺️ Roadmap

| Phase | Description | Status |
|---|---|---|
| 1 | Environment: Python venv, PostgreSQL, config via `.env` | ✅ Complete |
| 2 | Business requirements, data sources, data contracts, data dictionary | ✅ Complete |
| 3 | Source data generation, verification and quality injection | ✅ Complete |
| 4 | **Bronze**: raw ingestion into PostgreSQL with audit metadata | 🔄 Next |
| 5 | **Silver**: contract validation, deduplication, quarantine | ⏳ Planned |
| 6 | **Gold**: facts, dimensions and business KPIs | ⏳ Planned |
| 7 | Incremental loads (watermarks) and idempotent re-runs | ⏳ Planned |
| 8 | Scale-out processing with PySpark | ⏳ Planned |
| 9 | Orchestration (Airflow) and Docker | ⏳ Planned |
| 10 | Cloud storage / deployment and streaming | ⏳ Planned |

---

## 📁 Project Structure

```text
retailpulse-data-platform/
├── docs/
│   ├── business_requirements.md
│   ├── data_contracts.md
│   ├── data_dictionary.md
│   └── data_sources.md
├── src/retailpulse/
│   ├── config.py                  # loads DB settings from .env
│   ├── db_test.py                 # PostgreSQL connectivity check
│   ├── db_health.py               # connectivity check with detailed error handling
│   ├── utils/system_info.py
│   └── data_generation/
│       ├── config.py              # seeds, sizes, catalogs, distributions
│       ├── customers.py  products.py  orders.py
│       ├── payments.py   shipments.py marketing.py
│       ├── injector_config.py     # declarative data-quality rules
│       ├── quality_injector.py    # writes *_dirty.csv files
│       └── *_verification.py      # per-dataset validation checks
├── data/                          # generated locally, git-ignored
├── .env.example
└── requirements.txt
```

---

## 🚀 Getting Started

**Prerequisites:** Python 3.10+, PostgreSQL, Git.

```powershell
# 1. Clone
git clone https://github.com/Bharatv05/retailpulse-data-platform.git
cd retailpulse-data-platform

# 2. Virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1          # macOS/Linux: source .venv/bin/activate

# 3. Dependencies
pip install -r requirements.txt

# 4. Configuration
copy .env.example .env              # macOS/Linux: cp .env.example .env
```

Edit `.env` with your local PostgreSQL details, then create the database:

```sql
CREATE DATABASE retailpulse;
```

Check the connection:

```powershell
$env:PYTHONPATH = "src"             # macOS/Linux: export PYTHONPATH=src
python -m retailpulse.db_test
```

### Generate the source data
Run from the repository root, in dependency order:

```powershell
python -m retailpulse.data_generation.customers
python -m retailpulse.data_generation.products
python -m retailpulse.data_generation.orders      # needs customers + products
python -m retailpulse.data_generation.payments    # needs orders
python -m retailpulse.data_generation.shipments   # needs orders
python -m retailpulse.data_generation.marketing   # needs customers
```

### Inject data-quality issues

```powershell
python -m retailpulse.data_generation.quality_injector
```

### Verify

```powershell
python -m retailpulse.data_generation.data_verification
python -m retailpulse.data_generation.orders_Verification
python -m retailpulse.data_generation.payment_verification
python -m retailpulse.data_generation.shipping_verification
python -m retailpulse.data_generation.marketing_verification
```

---

## 🧭 Engineering Principles

- **Docs and contracts before code:** every dataset has a defined grain, schema and rule set.
- **Raw data is never modified:** every downstream issue can be fixed by reprocessing.
- **Known-answer testing:** clean and dirty versions of the same data make data-quality checks measurable.
- **Idempotent by design:** re-running a load must not create duplicate business records.
- **Secrets stay out of Git:** credentials come from `.env`, which is git-ignored.

---

## 👤 Author

**Bharat V**, Data Engineer · [GitHub](https://github.com/Bharatv05)
