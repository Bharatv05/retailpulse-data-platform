# src/retailpulse/data_generation/shipments.py

from datetime import datetime, timedelta

import numpy  as np
import pandas as pd

from retailpulse.data_generation.config import (
    CARRIERS,
    DELIVERY_WINDOW_MAX,
    DELIVERY_WINDOW_MIN,
    ORDERS_SOURCE_DIR,
    RANDOM_SEED,
    SHIPMENT_STATUS_MAP,
    SHIPMENTS_SOURCE_DIR,
)

# ── ID Helper ──────────────────────────────────────────────────────────────────

def generate_shipment_id(index: int) -> str:
    """SH00000001, SH00000002 ..."""
    return f"SH{index:08d}"


# ── Timestamp Helper ───────────────────────────────────────────────────────────

def generate_timestamps(
    shipment_date : datetime,
    rng           : np.random.Generator,
) -> tuple[datetime, datetime]:
    """
    created_at = shipment_date
    updated_at = created_at + 0 to 12 hours
    updated_at >= created_at guaranteed by construction.
    """
    created_at = shipment_date
    updated_at = created_at + timedelta(hours=int(rng.integers(0, 13)))
    return created_at, updated_at


# ── Dependency Loader ──────────────────────────────────────────────────────────

def load_eligible_orders() -> pd.DataFrame:
    """
    Load orders that require a shipment record.

    Eligible statuses: CONFIRMED, SHIPPED, DELIVERED
    Excluded statuses: PENDING, CANCELLED

    We need: order_id, order_date, order_status
    """
    path = ORDERS_SOURCE_DIR / "orders.csv"
    df   = pd.read_csv(
        path,
        usecols=["order_id", "order_date", "order_status"],
        parse_dates=["order_date"],
    )

    eligible = df[df["order_status"].isin(["CONFIRMED", "SHIPPED", "DELIVERED"])]
    return eligible.reset_index(drop=True)


# ── Generator ──────────────────────────────────────────────────────────────────

def generate_shipments() -> pd.DataFrame:

    rng            = np.random.default_rng(RANDOM_SEED)
    eligible_df    = load_eligible_orders()

    print(f"   Eligible orders   : {len(eligible_df):,}")
    print(f"   (CONFIRMED + SHIPPED + DELIVERED only)")

    records = []

    for idx, row in eligible_df.iterrows():

        order_id       = row["order_id"]
        order_status   = row["order_status"]
        order_date     = row["order_date"]

        # ── Shipment Date ──────────────────────────────────────────────────────
        # Shipment leaves warehouse 1–3 days after order date
        shipment_date = order_date + timedelta(
            days=int(rng.integers(1, 4))
        )

        # ── Expected Delivery Date ─────────────────────────────────────────────
        delivery_window      = int(rng.integers(DELIVERY_WINDOW_MIN, DELIVERY_WINDOW_MAX + 1))
        expected_delivery_dt = shipment_date + timedelta(days=delivery_window)

        # ── Actual Delivery Date ───────────────────────────────────────────────
        # Only DELIVERED orders have an actual delivery date
        # IN_TRANSIT and PROCESSING → NULL (unknown future date)
        if order_status == "DELIVERED":
            # Actual delivery is on or before expected delivery date
            # (can arrive 0–2 days early)
            early_days           = int(rng.integers(0, 3))
            actual_delivery_date = expected_delivery_dt - timedelta(days=early_days)

            # Safety — actual delivery cannot be before shipment date
            if actual_delivery_date < shipment_date:
                actual_delivery_date = shipment_date
        else:
            actual_delivery_date = None     # NULL for IN_TRANSIT / PROCESSING

        # ── Shipment Status ────────────────────────────────────────────────────
        shipment_status = SHIPMENT_STATUS_MAP[order_status]

        # ── Carrier ───────────────────────────────────────────────────────────
        carrier = str(rng.choice(CARRIERS))

        # ── Timestamps ────────────────────────────────────────────────────────
        created_at, updated_at = generate_timestamps(shipment_date, rng)

        records.append({
            "shipment_id"           : generate_shipment_id(idx + 1),
            "order_id"              : order_id,
            "shipment_status"       : shipment_status,
            "carrier"               : carrier,
            "shipment_date"         : shipment_date.date(),
            "expected_delivery_date": expected_delivery_dt.date(),
            "actual_delivery_date"  : (
                actual_delivery_date.date()
                if actual_delivery_date is not None
                else None
            ),
            "created_at"            : created_at,
            "updated_at"            : updated_at,
        })

    return pd.DataFrame(records)


# ── Save ───────────────────────────────────────────────────────────────────────

def save_shipments(df: pd.DataFrame) -> None:
    SHIPMENTS_SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    path = SHIPMENTS_SOURCE_DIR / "shipments.csv"
    df.to_csv(path, index=False)
    print(f"\n✅ Shipments saved    → {path}")
    print(f"   Rows written       : {len(df):,}")


# ── Entry Point ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("🔄 Generating shipments dataset...")
    shipments_df = generate_shipments()
    save_shipments(shipments_df)