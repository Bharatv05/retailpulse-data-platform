# RetailPulse Data Dictionary

## 1. Purpose

The data dictionary describes the important fields used by the RetailPulse data platform.

It provides a common understanding of:

* Column names
* Data types
* Nullability
* Business meaning
* Dataset grain

The dictionary will be expanded as the project develops and the final datasets are generated.

---

# 2. Customers

### Dataset Grain

One row represents one customer.

| Column          | Data Type | Nullable | Description                        |
| --------------- | --------- | -------- | ---------------------------------- |
| customer_id     | string    | No       | Unique identifier for the customer |
| customer_name   | string    | No       | Customer's full name               |
| email           | string    | No       | Customer email address             |
| phone           | string    | Yes      | Customer contact number            |
| city            | string    | Yes      | Customer city                      |
| state           | string    | Yes      | Customer state/region              |
| country         | string    | Yes      | Customer country                   |
| signup_date     | date      | No       | Date the customer registered       |
| customer_status | string    | No       | Current customer status            |

---

# 3. Products

### Dataset Grain

One row represents one product.

| Column              | Data Type | Nullable | Description                       |
| ------------------- | --------- | -------- | --------------------------------- |
| product_id          | string    | No       | Unique identifier for the product |
| product_name        | string    | No       | Product name                      |
| category            | string    | No       | Main product category             |
| subcategory         | string    | Yes      | Product subcategory               |
| brand               | string    | Yes      | Product brand                     |
| unit                | string    | No       | Unit in which the product is sold |
| unit_price          | decimal   | No       | Current product unit price        |
| discount_percentage | decimal   | Yes      | Applicable discount percentage    |
| product_status      | string    | No       | Current product status            |

---

# 4. Orders

### Dataset Grain

One row represents one product line within an order.

| Column          | Data Type | Nullable | Description                                      |
| --------------- | --------- | -------- | ------------------------------------------------ |
| order_id        | string    | No       | Unique identifier for the customer order         |
| customer_id     | string    | No       | Identifier of the customer who placed the order  |
| product_id      | string    | No       | Identifier of the purchased product              |
| order_date      | date      | No       | Date the order was placed                        |
| quantity        | integer   | No       | Number of units purchased                        |
| unit_price      | decimal   | No       | Price per unit at the time of the order          |
| discount_amount | decimal   | Yes      | Discount applied to the order line               |
| order_status    | string    | No       | Current status of the order                      |
| sales_channel   | string    | No       | Channel through which the order was placed       |
| created_at      | timestamp | No       | Timestamp when the order record was created      |
| updated_at      | timestamp | No       | Timestamp when the order record was last updated |

---

# 5. Payments

### Dataset Grain

One row represents one payment transaction.

| Column            | Data Type | Nullable | Description                          |
| ----------------- | --------- | -------- | ------------------------------------ |
| payment_id        | string    | No       | Unique identifier for the payment    |
| order_id          | string    | No       | Identifier of the related order      |
| payment_method    | string    | No       | Method used for payment              |
| payment_status    | string    | No       | Current payment status               |
| payment_amount    | decimal   | No       | Amount associated with the payment   |
| payment_timestamp | timestamp | No       | Timestamp of the payment transaction |

---

# 6. Shipments

### Dataset Grain

One row represents one shipment.

| Column                 | Data Type | Nullable | Description                            |
| ---------------------- | --------- | -------- | -------------------------------------- |
| shipment_id            | string    | No       | Unique identifier for the shipment     |
| order_id               | string    | No       | Identifier of the related order        |
| warehouse_id           | string    | Yes      | Warehouse responsible for the shipment |
| shipped_date           | date      | No       | Date the shipment was dispatched       |
| expected_delivery_date | date      | Yes      | Expected delivery date                 |
| delivered_date         | date      | Yes      | Actual delivery date                   |
| shipment_status        | string    | No       | Current shipment status                |

---

# 7. Marketing Campaign Performance

### Dataset Grain

One row represents one campaign performance record for a defined reporting period.

| Column             | Data Type | Nullable | Description                                |
| ------------------ | --------- | -------- | ------------------------------------------ |
| campaign_id        | string    | No       | Unique identifier for the campaign         |
| campaign_name      | string    | No       | Name of the marketing campaign             |
| marketing_channel  | string    | No       | Channel used for the campaign              |
| campaign_date      | date      | No       | Reporting date for campaign performance    |
| impressions        | integer   | No       | Number of times the campaign was displayed |
| clicks             | integer   | No       | Number of clicks generated                 |
| conversions        | integer   | No       | Number of conversions generated            |
| spend              | decimal   | No       | Marketing expenditure                      |
| attributed_revenue | decimal   | Yes      | Revenue attributed to the campaign         |

---

# 8. Important Business Keys

| Dataset                        | Business Key                |
| ------------------------------ | --------------------------- |
| Customers                      | customer_id                 |
| Products                       | product_id                  |
| Orders                         | order_id + product_id       |
| Payments                       | payment_id                  |
| Shipments                      | shipment_id                 |
| Marketing Campaign Performance | campaign_id + campaign_date |

These keys represent the initial design and may be refined when the actual source datasets are generated and analyzed.

---

# 9. Important Relationships

```text
Customer
   │
   │ customer_id
   ↓
Orders
   │
   │ product_id
   ↓
Product
```

```text
Orders
   │
   ├────────→ Payments
   │
   └────────→ Shipments
```

```text
Marketing Campaign
        │
        ↓
Campaign Performance
```

---

# 10. Important Grain Definitions

The grain of each dataset must be understood before designing downstream tables.

```text
Customers
→ One row = one customer

Products
→ One row = one product

Orders
→ One row = one product line within an order

Payments
→ One row = one payment transaction

Shipments
→ One row = one shipment

Marketing
→ One row = one campaign performance record for a reporting period
```

The grain must remain explicit when datasets are transformed into staging, analytical, and warehouse structures.
