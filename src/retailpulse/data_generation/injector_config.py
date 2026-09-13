# src/retailpulse/data_generation/injector_config.py

"""
Injection rules for every dataset.
Each rule defines:
  - rate     : fraction of rows affected (0.01 = 1%)
  - problem  : short identifier used in logging
"""

CUSTOMER_INJECTION_RULES = [
    {"problem": "null_email",               "rate": 0.03},
    {"problem": "invalid_email_format",     "rate": 0.01},
    {"problem": "duplicate_record",         "rate": 0.01},
    {"problem": "invalid_phone",            "rate": 0.01},
    {"problem": "timestamp_reversal",       "rate": 0.005},
]

PRODUCT_INJECTION_RULES = [
    {"problem": "null_unit_price",          "rate": 0.01},
    {"problem": "invalid_discount",         "rate": 0.01},
    {"problem": "invalid_category_combo",   "rate": 0.01},
    {"problem": "duplicate_record",         "rate": 0.005},
    {"problem": "invalid_status",           "rate": 0.005},
]

ORDER_INJECTION_RULES = [
    {"problem": "null_customer_id",         "rate": 0.01},
    {"problem": "duplicate_record",         "rate": 0.01},
    {"problem": "invalid_order_status",     "rate": 0.01},
    {"problem": "negative_total_amount",    "rate": 0.005},
    {"problem": "timestamp_reversal",       "rate": 0.005},
]

ORDER_ITEM_INJECTION_RULES = [
    {"problem": "invalid_product_id",       "rate": 0.01},
    {"problem": "invalid_order_id",         "rate": 0.005},
    {"problem": "zero_negative_quantity",   "rate": 0.01},
    {"problem": "incorrect_total_price",    "rate": 0.01},
    {"problem": "duplicate_record",         "rate": 0.005},
]

PAYMENT_INJECTION_RULES = [
    {"problem": "invalid_order_id",         "rate": 0.005},
    {"problem": "amount_mismatch",          "rate": 0.01},
    {"problem": "invalid_payment_status",   "rate": 0.01},
    {"problem": "duplicate_record",         "rate": 0.005},
    {"problem": "null_payment_method",      "rate": 0.01},
]

SHIPMENT_INJECTION_RULES = [
    {"problem": "invalid_order_id",         "rate": 0.005},
    {"problem": "invalid_date_sequence",    "rate": 0.01},
    {"problem": "invalid_shipment_status",  "rate": 0.01},
    {"problem": "missing_delivered_date",   "rate": 0.01},
]

CAMPAIGN_INJECTION_RULES = [
    {"problem": "invalid_date_range",       "rate": 0.01},
    {"problem": "invalid_budget",           "rate": 0.01},
    {"problem": "invalid_status",           "rate": 0.01},
    {"problem": "duplicate_record",         "rate": 0.005},
]

CAMPAIGN_CUSTOMER_INJECTION_RULES = [
    {"problem": "invalid_campaign_id",      "rate": 0.005},
    {"problem": "invalid_customer_id",      "rate": 0.01},
    {"problem": "duplicate_pair",           "rate": 0.02},
    {"problem": "invalid_conversion_date",  "rate": 0.01},
    {"problem": "false_converted_with_date","rate": 0.01},
]

# Invalid values used across injectors
INVALID_STATUS_VALUES    = ["unknown", "INVALID", "N/A", "pending_review", "ERROR"]
INVALID_SHIPMENT_STATUSES = ["UNKNOWN", "IN_PROGRESS", "PENDING", "ERROR"]
INVALID_PAYMENT_STATUSES  = ["PROCESSING", "UNKNOWN", "RETRY", "ERROR"]
INVALID_ORDER_STATUSES    = ["PROCESSING", "UNKNOWN", "IN_REVIEW", "ERROR"]
INVALID_CAMPAIGN_STATUSES = ["RUNNING", "UNKNOWN", "DRAFT", "ERROR"]