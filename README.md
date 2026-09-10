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

