# RetailPulse Data Sources

## 1. Overview

RetailPulse receives data from multiple heterogeneous sources.

The initial platform will use a combination of:

* CSV files
* JSON files
* Excel files
* PostgreSQL
* REST API

Each source has different formats, update frequencies, schemas, and potential data-quality problems.

The purpose of documenting these sources is to understand the data before implementing ingestion and transformation pipelines.

---

## 2. Customer Data

### Source

Customer operational system

### Format

CSV

### File

`customers.csv`

### Frequency

Daily

### Historical Availability

Historical customer records will be available for the initial load.

### Grain

One row represents one customer.

### Important Fields

* customer_id
* customer_name
* email
* phone
* city
* state
* country
* signup_date
* customer_status

### Potential Data Quality Problems

* Missing customer_id
* Duplicate customer_id
* Missing email
* Invalid email format
* Missing location information
* Inconsistent customer status values
* Incorrect date formats
* Changed customer information

---

## 3. Product Data

### Source

Product/catalog system

### Format

CSV

### File

`products.csv`

### Frequency

Daily

### Historical Availability

Historical product information will be available.

### Grain

One row represents one product.

### Important Fields

* product_id
* product_name
* category
* subcategory
* brand
* unit
* unit_price
* discount_percentage
* product_status

### Potential Data Quality Problems

* Missing product_id
* Duplicate product_id
* Missing product name
* Invalid price
* Negative price
* Invalid discount percentage
* Inconsistent category names
* Inconsistent product naming
* Incorrect data types

### Note

Inventory information is intentionally not part of the initial product grain.

If inventory snapshots are introduced later, the grain will be explicitly defined separately, for example:

> One row represents the inventory quantity of one product at a specific point in time.

---

## 4. Order Data

### Source

E-commerce order system

### Format

CSV

### File

`orders.csv`

### Frequency

Daily

### Historical Availability

Historical order data will be available for the initial load.

### Grain

One row represents one product line within an order.

Therefore, a single order may contain multiple rows.

Example:

```text
order_id | product_id | quantity
---------|------------|---------
O1001    | P001       | 2
O1001    | P002       | 1
O1001    | P003       | 4
```

### Important Fields

* order_id
* customer_id
* product_id
* order_date
* quantity
* unit_price
* discount_amount
* order_status
* sales_channel
* created_at
* updated_at

### Potential Data Quality Problems

* Duplicate order lines
* Missing customer_id
* Missing product_id
* Invalid quantity
* Negative quantity
* Invalid price
* Invalid order status
* Invalid timestamps
* Duplicate exports
* Late-arriving records
* Updated historical records

---

## 5. Payment Data

### Source

Payment processing system

### Format

JSON

### File

`payments.json`

### Frequency

Daily

### Historical Availability

Historical payment transactions will be available.

### Grain

One row represents one payment transaction.

### Important Fields

* payment_id
* order_id
* payment_method
* payment_status
* payment_amount
* payment_timestamp

### Potential Data Quality Problems

* Duplicate payment_id
* Missing order_id
* Invalid payment amount
* Invalid payment status
* Incorrect timestamp format
* Failed or incomplete transactions

---

## 6. Shipment Data

### Source

Logistics/shipping system

### Format

Excel

### File

`shipments.xlsx`

### Frequency

Daily

### Historical Availability

Historical shipment records will be available.

### Grain

One row represents one shipment.

### Important Fields

* shipment_id
* order_id
* warehouse_id
* shipped_date
* expected_delivery_date
* delivered_date
* shipment_status

### Potential Data Quality Problems

* Duplicate shipment_id
* Missing order_id
* Missing shipment dates
* Delivered date earlier than shipped date
* Invalid shipment status
* Incorrect date formats
* Late-arriving shipment updates

---

## 7. Marketing Data

### Source

External marketing platform

### Format

REST API / JSON response

### Endpoint

A simulated marketing API will be used during the project.

### Frequency

Daily

### Historical Availability

Historical campaign performance data will be available where supported.

### Grain

One row represents one campaign performance record for a defined reporting period.

### Important Fields

* campaign_id
* campaign_name
* marketing_channel
* campaign_date
* impressions
* clicks
* conversions
* spend
* attributed_revenue

### Potential Data Quality Problems

* Missing campaign_id
* Duplicate campaign records
* Invalid metrics
* Negative spend
* Invalid timestamps
* Missing campaign names
* API response schema changes
* API failures
* Partial API responses

---

## 8. Source Summary

| Source    | Format          | Frequency | Grain                      |
| --------- | --------------- | --------- | -------------------------- |
| Customers | CSV             | Daily     | One customer               |
| Products  | CSV             | Daily     | One product                |
| Orders    | CSV             | Daily     | One order line             |
| Payments  | JSON            | Daily     | One payment transaction    |
| Shipments | Excel           | Daily     | One shipment               |
| Marketing | REST API / JSON | Daily     | One campaign-period record |

---

## 9. Initial Ingestion Strategy

The initial ingestion layer will use Python.

Conceptually:

```text
CSV
 ↓
Python ingestion

JSON
 ↓
Python ingestion

Excel
 ↓
Python ingestion

PostgreSQL
 ↓
Python database extraction

REST API
 ↓
Python API client
```

The raw source data will be preserved before major transformations are applied.

---

## 10. Source Reliability Considerations

The pipeline should not assume that every source is always available or correct.

Potential failures include:

* Missing files
* Empty files
* Corrupted files
* API timeout
* API authentication failure
* API schema change
* Database connection failure
* Duplicate source delivery
* Partial data delivery

These scenarios will be introduced and handled progressively in later phases.
