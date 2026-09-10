# src/retailpulse/data_generation/products.py

import random
import uuid
from datetime import datetime, timedelta

import numpy  as np
import pandas as pd

from retailpulse.data_generation.config import (
    BRANDS,
    CATEGORY_PRICE_RANGES,
    PRODUCT_CATALOG,
    PRODUCT_COUNT,
    PRODUCT_STATUS_WEIGHTS,
    PRODUCT_STATUSES,
    PRODUCTS_SOURCE_DIR,
    RANDOM_SEED,
    UNITS,
)

# ── Seed ──────────────────────────────────────────────────────────────────────

random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)

# ── Helpers ───────────────────────────────────────────────────────────────────

def generate_product_id(index: int) -> str:
    """
    Produces a zero-padded product ID.
    Example: P000001, P000002, ...
    """
    return f"P{index:06d}"


def generate_timestamps(rng: np.random.Generator) -> tuple[datetime, datetime]:
    """
    created_at → random date between 2020-01-01 and 2024-12-31
    updated_at → created_at + random offset (0 – 365 days)

    updated_at is always >= created_at.
    This is enforced by construction, not by a post-hoc check.
    """
    base_date   = datetime(2020, 1, 1)
    created_at  = base_date + timedelta(days=int(rng.integers(0, 5 * 365)))
    updated_at  = created_at + timedelta(days=int(rng.integers(0, 366)))
    return created_at, updated_at


# ── Generator ─────────────────────────────────────────────────────────────────

def generate_products(n: int = PRODUCT_COUNT) -> pd.DataFrame:

    rng      = np.random.default_rng(RANDOM_SEED)
    records  = []
    categories = list(PRODUCT_CATALOG.keys())

    for i in range(1, n + 1):

        # ── Category & Subcategory (controlled relationship) ──────────────────
        category    = rng.choice(categories)
        subcategory = rng.choice(PRODUCT_CATALOG[category])

        # ── Product Name ──────────────────────────────────────────────────────
        brand        = rng.choice(BRANDS)
        product_name = f"{brand} {subcategory}"

        # ── Price (category-aware) ────────────────────────────────────────────
        price_min, price_max = CATEGORY_PRICE_RANGES[category]
        unit_price           = round(float(rng.uniform(price_min, price_max)), 2)

        # ── Discount ──────────────────────────────────────────────────────────
        # 0% to 30% — realistic retail discount range
        discount_percentage = round(float(rng.uniform(0, 30)), 2)

        # ── Unit ──────────────────────────────────────────────────────────────
        unit = rng.choice(UNITS)

        # ── Status ────────────────────────────────────────────────────────────
        product_status = rng.choice(
            PRODUCT_STATUSES,
            p=PRODUCT_STATUS_WEIGHTS,
        )

        # ── Timestamps ────────────────────────────────────────────────────────
        created_at, updated_at = generate_timestamps(rng)

        records.append({
            "product_id":           generate_product_id(i),
            "product_name":         product_name,
            "category":             category,
            "subcategory":          subcategory,
            "brand":                brand,
            "unit":                 unit,
            "unit_price":           unit_price,
            "discount_percentage":  discount_percentage,
            "product_status":       product_status,
            "created_at":           created_at,
            "updated_at":           updated_at,
        })

    return pd.DataFrame(records)


# ── Save ──────────────────────────────────────────────────────────────────────

def save_products(df: pd.DataFrame) -> None:
    PRODUCTS_SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    output_path = PRODUCTS_SOURCE_DIR / "products.csv"
    df.to_csv(output_path, index=False)
    print(f"✅ Products saved → {output_path}")
    print(f"   Rows written : {len(df):,}")


# ── Entry Point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("🔄 Generating product dataset...")
    products_df = generate_products()
    save_products(products_df)