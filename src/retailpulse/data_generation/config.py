# src/retailpulse/data_generation/config.py

from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────────

PROJECT_ROOT = Path(__file__).resolve().parents[3]

DATA_SOURCE_DIR = PROJECT_ROOT / "data" / "source"

CUSTOMERS_SOURCE_DIR  = DATA_SOURCE_DIR / "customers"
PRODUCTS_SOURCE_DIR   = DATA_SOURCE_DIR / "products"
ORDERS_SOURCE_DIR     = DATA_SOURCE_DIR / "orders"
PAYMENTS_SOURCE_DIR   = DATA_SOURCE_DIR / "payments"
SHIPMENTS_SOURCE_DIR  = DATA_SOURCE_DIR / "shipments"
MARKETING_SOURCE_DIR  = DATA_SOURCE_DIR / "marketing"          # ← NEW

# ── Reproducibility ────────────────────────────────────────────────────────────

RANDOM_SEED = 42

# ── Dataset Sizes ──────────────────────────────────────────────────────────────

CUSTOMER_COUNT  = 10_000
PRODUCT_COUNT   = 1_000
ORDER_COUNT     = 40_000
CAMPAIGN_COUNT  = 50                                            # ← NEW

# ── Product Catalog ────────────────────────────────────────────────────────────

PRODUCT_CATALOG = {
    "Football":   ["Footballs", "Football Shoes", "Football Apparel", "Football Accessories"],
    "Cricket":    ["Cricket Bats", "Cricket Balls", "Cricket Apparel", "Cricket Protective Gear"],
    "Running":    ["Running Shoes", "Running Apparel", "Running Accessories"],
    "Tennis":     ["Tennis Rackets", "Tennis Balls", "Tennis Apparel", "Tennis Accessories"],
    "Basketball": ["Basketballs", "Basketball Shoes", "Basketball Apparel", "Basketball Accessories"],
}

# ── Category-Aware Price Ranges ────────────────────────────────────────────────

CATEGORY_PRICE_RANGES = {
    "Football":   (500,   8_000),
    "Cricket":    (300,  15_000),
    "Running":    (800,  12_000),
    "Tennis":     (400,  10_000),
    "Basketball": (600,   9_000),
}

# ── Brands ────────────────────────────────────────────────────────────────────

BRANDS = ["Nike", "Adidas", "Puma", "Under Armour", "Reebok", "Decathlon", "Asics"]

# ── Units ─────────────────────────────────────────────────────────────────────

UNITS = ["Piece", "Pair", "Set"]

# ── Product Status ────────────────────────────────────────────────────────────

PRODUCT_STATUSES       = ["ACTIVE", "DISCONTINUED"]
PRODUCT_STATUS_WEIGHTS = [0.90,     0.10]

# ── Order Status ───────────────────────────────────────────────────────────────

ORDER_STATUSES       = ["PENDING", "CONFIRMED", "SHIPPED", "DELIVERED", "CANCELLED"]
ORDER_STATUS_WEIGHTS = [0.08,      0.10,        0.15,      0.60,        0.07]

# ── Items Per Order ────────────────────────────────────────────────────────────

ITEMS_PER_ORDER_OPTIONS = [1,    2,    3,    4,    5,    6,    7,    8,     9,     10]
ITEMS_PER_ORDER_WEIGHTS = [0.35, 0.25, 0.18, 0.10, 0.05, 0.03, 0.02, 0.01, 0.005, 0.005]

# ── Quantity Per Line Item ─────────────────────────────────────────────────────

QUANTITY_OPTIONS = [1,    2,    3,    4,    5]
QUANTITY_WEIGHTS = [0.50, 0.25, 0.13, 0.07, 0.05]

# ── Payment ───────────────────────────────────────────────────────────────────

PAYMENT_METHODS        = ["UPI", "NET_BANKING", "CARD", "COD"]
PAYMENT_METHOD_WEIGHTS = [0.35,  0.20,          0.30,  0.15]
PAYMENT_FAILURE_RATE   = 0.05
PAYMENT_RETRY_RATE     = 0.70

# ── Shipments ─────────────────────────────────────────────────────────────────

CARRIERS = [
    "Delhivery", "BlueDart", "DTDC",
    "FedEx", "Ekart", "XpressBees", "India Post",
]

SHIPMENT_STATUS_MAP = {
    "CONFIRMED" : "PROCESSING",
    "SHIPPED"   : "IN_TRANSIT",
    "DELIVERED" : "DELIVERED",
}

DELIVERY_WINDOW_MIN = 2
DELIVERY_WINDOW_MAX = 7

# ── Marketing ─────────────────────────────────────────────────────────────── ← NEW

CAMPAIGN_CHANNELS         = ["EMAIL", "SMS", "SOCIAL_MEDIA", "PUSH_NOTIFICATION"]
CAMPAIGN_CHANNEL_WEIGHTS  = [0.35,    0.25,  0.25,           0.15]

CAMPAIGN_STATUSES         = ["ACTIVE", "COMPLETED", "PAUSED"]
CAMPAIGN_STATUS_WEIGHTS   = [0.20,     0.70,        0.10]
# Most campaigns in a historical dataset are already completed

# Budget range per campaign in INR
CAMPAIGN_BUDGET_MIN = 50_000
CAMPAIGN_BUDGET_MAX = 500_000

# What fraction of customers each campaign targets (10% to 40%)
CAMPAIGN_TARGET_RATE_MIN = 0.10
CAMPAIGN_TARGET_RATE_MAX = 0.40

# Conversion rate — % of targeted customers who make a purchase
CAMPAIGN_CONVERSION_RATE_MIN = 0.05     # 5%  minimum conversion
CAMPAIGN_CONVERSION_RATE_MAX = 0.30     # 30% maximum conversion