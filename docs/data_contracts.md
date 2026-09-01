# RetailPulse Data Contracts

## 1. Purpose

A data contract defines the expected structure and basic business rules for data entering the RetailPulse data platform.

The contract establishes expectations around:

* Dataset grain
* Required fields
* Data types
* Nullability
* Uniqueness
* Business rules
* Invalid data behavior

The contracts will later be used to build automated validation.

---

# 2. Customer Data Contract

## Dataset

`customers`

## Grain

One row represents one customer.

## Required Fields

* customer_id
* customer_name
* email
* signup_date

## Schema

| Column          | Type   | Nullable |
| --------------- | ------ | -------- |
| customer_id     | string | No       |
| customer_name   | string | No       |
| email           | string | No       |
| phone           | string | Yes      |
| city            | string | Yes      |
| state           | string | Yes      |
| country         | string | Yes      |
| signup_date     | date   | No       |
| customer_status | string | No       |

## Uniqueness Rules

`customer_id` must be unique.

## Business Rules

* customer_id must not be NULL.
* customer_name must not be NULL.
* email must not be NULL.
* email should follow a valid email format.
* signup_date must be a valid date.
* customer_status must contain an accepted status.

## Invalid Data Behavior

Invalid records should be identified and prevented from silently entering trusted analytical datasets.

---

# 3. Product Data Contract

## Dataset

`products`

## Grain

One row represents one product.

## Required Fields

* product_id
* product_name
* category
* unit_price
* product_status

## Schema

| Column              | Type    | Nullable |
| ------------------- | ------- | -------- |
| product_id          | string  | No       |
| product_name        | string  | No       |
| category            | string  | No       |
| subcategory         | string  | Yes      |
| brand               | string  | Yes      |
| unit                | string  | No       |
| unit_price          | decimal | No       |
| discount_percentage | decimal | Yes      |
| product_status      | string  | No       |

## Uniqueness Rules

`product_id` must be unique.

## Business Rules

* product_id must not be NULL.
* product_name must not be NULL.
* unit_price must be greater than or equal to zero.
* discount_percentage must be between 0 and 100.
* product_status must contain an accepted value.

## Invalid Data Behavior

Invalid product records should be identified during validation and should not be treated as trusted product data.

---

# 4. Order Data Contract

## Dataset

`orders`

## Grain

One row represents one product line within an order.

The business key for the initial design is:

```text
(order_id, product_id)
```

## Required Fields

* order_id
* customer_id
* product_id
* order_date
* quantity
* unit_price
* order_status
* created_at
* updated_at

## Schema

| Column          | Type      | Nullable |
| --------------- | --------- | -------- |
| order_id        | string    | No       |
| customer_id     | string    | No       |
| product_id      | string    | No       |
| order_date      | date      | No       |
| quantity        | integer   | No       |
| unit_price      | decimal   | No       |
| discount_amount | decimal   | Yes      |
| order_status    | string    | No       |
| sales_channel   | string    | No       |
| created_at      | timestamp | No       |
| updated_at      | timestamp | No       |

## Uniqueness Rules

The combination of:

```text
order_id + product_id
```

should identify an order line in the initial model.

## Referential Rules

* customer_id should exist in the customer dataset.
* product_id should exist in the product dataset.

## Business Rules

* quantity must be greater than zero.
* unit_price must be greater than or equal to zero.
* discount_amount must be greater than or equal to zero.
* order_date must be valid.
* updated_at must not be earlier than created_at.
* order_status must contain an accepted status.
* sales_channel must contain an accepted channel.

## Incremental Processing Rules

The initial historical load will process existing records.

Future incremental processing should identify newly created or changed records using appropriate timestamp/watermark logic.

The `order_date` field alone should not be assumed to identify updates because an order can be modified after its original order date.

## Invalid Data Behavior

Invalid records should be identified during validation and prevented from silently affecting analytical metrics.

---

# 5. Payment Data Contract

## Dataset

`payments`

## Grain

One row represents one payment transaction.

## Required Fields

* payment_id
* order_id
* payment_method
* payment_status
* payment_amount
* payment_timestamp

## Schema

| Column            | Type      | Nullable |
| ----------------- | --------- | -------- |
| payment_id        | string    | No       |
| order_id          | string    | No       |
| payment_method    | string    | No       |
| payment_status    | string    | No       |
| payment_amount    | decimal   | No       |
| payment_timestamp | timestamp | No       |

## Uniqueness Rules

`payment_id` must be unique.

## Referential Rules

`order_id` should exist in the order dataset.

## Business Rules

* payment_amount must be greater than or equal to zero.
* payment_status must contain an accepted value.
* payment_timestamp must be valid.

---

# 6. Shipment Data Contract

## Dataset

`shipments`

## Grain

One row represents one shipment.

## Required Fields

* shipment_id
* order_id
* shipped_date
* expected_delivery_date
* shipment_status

## Schema

| Column                 | Type   | Nullable |
| ---------------------- | ------ | -------- |
| shipment_id            | string | No       |
| order_id               | string | No       |
| warehouse_id           | string | Yes      |
| shipped_date           | date   | No       |
| expected_delivery_date | date   | Yes      |
| delivered_date         | date   | Yes      |
| shipment_status        | string | No       |

## Uniqueness Rules

`shipment_id` must be unique.

## Referential Rules

`order_id` should exist in the order dataset.

## Business Rules

* shipped_date must be a valid date.
* delivered_date must not be earlier than shipped_date.
* shipment_status must contain an accepted status.
* delivered_date may be NULL when the shipment has not yet been delivered.

---

# 7. Marketing Data Contract

## Dataset

`marketing_campaign_performance`

## Grain

One row represents one campaign performance record for a defined reporting period.

## Required Fields

* campaign_id
* campaign_name
* marketing_channel
* campaign_date
* impressions
* clicks
* conversions
* spend

## Schema

| Column             | Type    | Nullable |
| ------------------ | ------- | -------- |
| campaign_id        | string  | No       |
| campaign_name      | string  | No       |
| marketing_channel  | string  | No       |
| campaign_date      | date    | No       |
| impressions        | integer | No       |
| clicks             | integer | No       |
| conversions        | integer | No       |
| spend              | decimal | No       |
| attributed_revenue | decimal | Yes      |

## Business Rules

* campaign_id must not be NULL.
* impressions must be greater than or equal to zero.
* clicks must be greater than or equal to zero.
* conversions must be greater than or equal to zero.
* spend must be greater than or equal to zero.
* clicks should not exceed impressions.
* conversions should not exceed clicks.
* campaign_date must be valid.

---

# 8. Common Data Quality Rules

Across all datasets, the platform should check for:

* Missing required fields
* Duplicate records
* Invalid data types
* Invalid dates/timestamps
* Invalid numeric values
* Referential integrity violations
* Unexpected categorical values
* Schema changes
* Unexpected record counts

---

# 9. Schema Change Policy

If an incoming source changes an expected schema, the pipeline should not silently assume the new structure is valid.

Example:

Expected:

```text
customer_id → string
```

Incoming:

```text
customer_id → integer
```

The pipeline should detect the schema difference and produce a validation result.

Depending on the severity of the change, the record/dataset may be:

* Rejected
* Quarantined
* Accepted after an explicit transformation
* Allowed after the contract is updated

The exact implementation will be developed in the Data Quality phase.

---

# 10. Duplicate Data Policy

Duplicate records must not automatically be deleted without understanding the business meaning of the duplicate.

The pipeline should distinguish between:

* True duplicate records
* Legitimate repeated transactions
* Updated records
* Source-system retries
* Late-arriving records

The appropriate deduplication strategy will depend on the dataset grain and business key.

---

# 11. Contract Evolution

Data contracts are expected to evolve as the business and source systems change.

Changes to a contract should be documented and validated before being introduced into downstream processing.
