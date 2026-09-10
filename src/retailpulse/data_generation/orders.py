# src/retailpulse/data_generation/orders.py

from datetime import datetime, timedelta

import numpy  as np
import pandas as pd

from retailpulse.data_generation.config import (
    CUSTOMERS_SOURCE_DIR,
    ITEMS_PER_ORDER_OPTIONS,
    ITEMS_PER_ORDER_WEIGHTS,
    ORDER_COUNT,
    ORDER_STATUSES,
    ORDER_STATUS_WEIGHTS,
    ORDERS_SOURCE_DIR,
    PRODUCTS_SOURCE_DIR,
    QUANTITY_OPTIONS,
    QUANTITY_WEIGHTS,
    RANDOM_SEED,
)

# ── ID Helpers ─────────────────────────────────────────────────────────────────

def generate_order_id(index: int) -> str:
    """O0000001, O0000002 ..."""
    return f"O{index:07d}"


def generate_order_item_id(index: int) -> str:
    """OI00000001, OI00000002 ..."""
    return f"OI{index:08d}"


# ── Timestamp Helper ───────────────────────────────────────────────────────────

def generate_timestamps(
    rng: np.random.Generator,
    order_date: datetime,
) -> tuple[datetime, datetime]:
    """
    created_at = order_date
    updated_at = created_at + small random offset (0–72 hours)

    updated_at >= created_at is guaranteed by construction.
    """
    created_at = order_date
    updated_at = created_at + timedelta(hours=int(rng.integers(0, 73)))
    return created_at, updated_at


# ── Dependency Loaders ─────────────────────────────────────────────────────────

def load_customer_ids() -> np.ndarray:
    """
    Load customer IDs from the generated customer master.
    Orders must reference REAL customers — not invented IDs.
    """
    path = CUSTOMERS_SOURCE_DIR / "customers.csv"
    df   = pd.read_csv(path, usecols=["customer_id"])
    return df["customer_id"].to_numpy()


def load_active_products() -> pd.DataFrame:
    """
    Load only ACTIVE products from the product master.
    New orders should not reference discontinued products.
    Returns a DataFrame with product_id and unit_price.
    """
    path = PRODUCTS_SOURCE_DIR / "products.csv"
    df   = pd.read_csv(path, usecols=["product_id", "unit_price", "product_status"])
    return (
        df[df["product_status"] == "ACTIVE"][["product_id", "unit_price"]]
        .reset_index(drop=True)
    )


# ── Generator ──────────────────────────────────────────────────────────────────

def generate_orders(n: int = ORDER_COUNT) -> tuple[pd.DataFrame, pd.DataFrame]:

    rng = np.random.default_rng(RANDOM_SEED)

    # ── Load Dependencies ──────────────────────────────────────────────────────
    customer_ids       = load_customer_ids()
    active_products_df = load_active_products()
    active_product_ids = active_products_df["product_id"].to_numpy()

    # Build a price lookup: product_id → unit_price
    price_lookup = dict(
        zip(active_products_df["product_id"], active_products_df["unit_price"])
    )

    print(f"   Customers loaded  : {len(customer_ids):,}")
    print(f"   Active products   : {len(active_product_ids):,}")

    # ── Output Containers ──────────────────────────────────────────────────────
    order_records      = []
    order_item_records = []
    order_item_counter = 1

    # ── Order Date Range ───────────────────────────────────────────────────────
    # Three years of history: 2022-01-01 → 2024-12-31
    start_date     = datetime(2022, 1, 1)
    date_range_days = (datetime(2024, 12, 31) - start_date).days

    # ── Main Loop ──────────────────────────────────────────────────────────────
    for i in range(1, n + 1):

        order_id    = generate_order_id(i)
        customer_id = str(rng.choice(customer_ids))
        order_date  = start_date + timedelta(days=int(rng.integers(0, date_range_days + 1)))

        # ── Number of items (weighted, 1–10) ───────────────────────────────────
        n_items = int(
            rng.choice(ITEMS_PER_ORDER_OPTIONS, p=ITEMS_PER_ORDER_WEIGHTS)
        )

        # Safeguard: cannot pick more items than available active products
        n_items = min(n_items, len(active_product_ids))

        # ── Sample UNIQUE products for this order (no replacement) ─────────────
        selected_products = rng.choice(
            active_product_ids,
            size=n_items,
            replace=False,         # ← enforces Option B: no duplicate products per order
        )

        # ── Build Order Items ──────────────────────────────────────────────────
        order_total = 0.0

        for product_id in selected_products:

            unit_price  = float(price_lookup[product_id])
            quantity    = int(rng.choice(QUANTITY_OPTIONS, p=QUANTITY_WEIGHTS))
            total_price = round(quantity * unit_price, 2)
            order_total += total_price

            item_created_at, item_updated_at = generate_timestamps(rng, order_date)

            order_item_records.append({
                "order_item_id" : generate_order_item_id(order_item_counter),
                "order_id"      : order_id,
                "product_id"    : product_id,
                "quantity"      : quantity,
                "unit_price"    : unit_price,
                "total_price"   : total_price,
                "created_at"    : item_created_at,
                "updated_at"    : item_updated_at,
            })

            order_item_counter += 1

        # ── Build Order Header ─────────────────────────────────────────────────
        order_status                  = str(rng.choice(ORDER_STATUSES, p=ORDER_STATUS_WEIGHTS))
        order_created_at, order_updated_at = generate_timestamps(rng, order_date)

        order_records.append({
            "order_id"     : order_id,
            "customer_id"  : customer_id,
            "order_date"   : order_date.date(),
            "order_status" : order_status,
            "total_amount" : round(order_total, 2),
            "created_at"   : order_created_at,
            "updated_at"   : order_updated_at,
        })

    orders_df      = pd.DataFrame(order_records)
    order_items_df = pd.DataFrame(order_item_records)

    return orders_df, order_items_df


# ── Save ───────────────────────────────────────────────────────────────────────

def save_orders(orders_df: pd.DataFrame, order_items_df: pd.DataFrame) -> None:

    ORDERS_SOURCE_DIR.mkdir(parents=True, exist_ok=True)

    orders_path      = ORDERS_SOURCE_DIR / "orders.csv"
    order_items_path = ORDERS_SOURCE_DIR / "order_items.csv"

    orders_df.to_csv(orders_path,      index=False)
    order_items_df.to_csv(order_items_path, index=False)

    print(f"\n✅ Orders saved       → {orders_path}")
    print(f"   Rows written       : {len(orders_df):,}")
    print(f"\n✅ Order items saved  → {order_items_path}")
    print(f"   Rows written       : {len(order_items_df):,}")
    print(f"\n   Avg items/order    : {len(order_items_df)/len(orders_df):.2f}")


# ── Entry Point ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("🔄 Generating orders dataset...")
    orders_df, order_items_df = generate_orders()
    save_orders(orders_df, order_items_df)