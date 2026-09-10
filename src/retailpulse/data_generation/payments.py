# src/retailpulse/data_generation/payments.py

from datetime import datetime, timedelta

import numpy  as np
import pandas as pd

from retailpulse.data_generation.config import (
    ORDERS_SOURCE_DIR,
    PAYMENT_FAILURE_RATE,
    PAYMENT_METHOD_WEIGHTS,
    PAYMENT_METHODS,
    PAYMENT_RETRY_RATE,
    PAYMENTS_SOURCE_DIR,
    RANDOM_SEED,
)

# ── ID Helper ──────────────────────────────────────────────────────────────────

def generate_payment_id(index: int) -> str:
    """PY00000001, PY00000002 ..."""
    return f"PY{index:08d}"


# ── Timestamp Helper ───────────────────────────────────────────────────────────

def generate_payment_date(
    rng: np.random.Generator,
    order_date: pd.Timestamp,
) -> datetime:
    """
    Payment date = order_date + 0 to 3 days.
    A customer typically pays on the same day or within a few days.
    Payment date is always >= order_date by construction.
    """
    return order_date + timedelta(days=int(rng.integers(0, 4)))


def generate_timestamps(
    payment_date: datetime,
    rng: np.random.Generator,
    retried: bool,
) -> tuple[datetime, datetime]:
    """
    created_at = payment_date
    updated_at:
      - No retry → small offset (0–6 hours)
      - Retried   → larger offset (1–48 hours) reflecting the retry window
    """
    created_at = payment_date
    if retried:
        updated_at = created_at + timedelta(hours=int(rng.integers(1, 49)))
    else:
        updated_at = created_at + timedelta(hours=int(rng.integers(0, 7)))
    return created_at, updated_at


# ── Dependency Loader ──────────────────────────────────────────────────────────

def load_orders() -> pd.DataFrame:
    """
    Load the order master.
    We need: order_id, order_date, order_status, total_amount.
    """
    path = ORDERS_SOURCE_DIR / "orders.csv"
    df   = pd.read_csv(
        path,
        usecols=["order_id", "order_date", "order_status", "total_amount"],
        parse_dates=["order_date"],
    )
    return df


# ── Core Status Logic ──────────────────────────────────────────────────────────

def determine_payment_status(
    order_status : str,
    method       : str,
    is_failed    : bool,
    is_retried   : bool,
) -> str:
    """
    Applies the business rule matrix:

    CANCELLED  + COD              → CANCELLED
    CANCELLED  + online           → REFUNDED
    DELIVERED  + any              → COMPLETED
    PENDING / CONFIRMED / SHIPPED + COD    → PENDING
    PENDING / CONFIRMED / SHIPPED + online → COMPLETED
    Failed online (not retried)            → FAILED
    Failed online (retried successfully)   → COMPLETED
    """
    if is_failed and not is_retried:
        return "FAILED"

    if order_status == "CANCELLED":
        return "CANCELLED" if method == "COD" else "REFUNDED"

    if method == "COD" and order_status in {"PENDING", "CONFIRMED", "SHIPPED"}:
        return "PENDING"

    return "COMPLETED"


# ── Generator ──────────────────────────────────────────────────────────────────

def generate_payments() -> pd.DataFrame:

    rng       = np.random.default_rng(RANDOM_SEED)
    orders_df = load_orders()

    print(f"   Orders loaded     : {len(orders_df):,}")

    online_methods = {"UPI", "NET_BANKING", "CARD"}
    records        = []

    for idx, row in orders_df.iterrows():

        payment_id     = generate_payment_id(idx + 1)
        order_id       = row["order_id"]
        order_status   = row["order_status"]
        payment_amount = row["total_amount"]
        order_date     = row["order_date"]

        # ── Payment Method ─────────────────────────────────────────────────────
        method = str(rng.choice(PAYMENT_METHODS, p=PAYMENT_METHOD_WEIGHTS))

        # ── Failure Logic (online only) ────────────────────────────────────────
        is_failed  = False
        is_retried = False

        if method in online_methods and order_status != "CANCELLED":
            is_failed = bool(rng.random() < PAYMENT_FAILURE_RATE)
            if is_failed:
                is_retried = bool(rng.random() < PAYMENT_RETRY_RATE)

        # ── Payment Status ─────────────────────────────────────────────────────
        payment_status = determine_payment_status(
            order_status, method, is_failed, is_retried
        )

        # ── Payment Date ───────────────────────────────────────────────────────
        payment_date = generate_payment_date(rng, order_date)

        # ── Timestamps ────────────────────────────────────────────────────────
        created_at, updated_at = generate_timestamps(payment_date, rng, is_retried)

        records.append({
            "payment_id"      : payment_id,
            "order_id"        : order_id,
            "payment_method"  : method,
            "payment_status"  : payment_status,
            "payment_amount"  : payment_amount,
            "payment_date"    : payment_date.date(),
            "payment_retried" : is_retried,
            "created_at"      : created_at,
            "updated_at"      : updated_at,
        })

    return pd.DataFrame(records)


# ── Save ───────────────────────────────────────────────────────────────────────

def save_payments(df: pd.DataFrame) -> None:
    PAYMENTS_SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    path = PAYMENTS_SOURCE_DIR / "payments.csv"
    df.to_csv(path, index=False)
    print(f"\n✅ Payments saved     → {path}")
    print(f"   Rows written       : {len(df):,}")


# ── Entry Point ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("🔄 Generating payments dataset...")
    payments_df = generate_payments()
    save_payments(payments_df)