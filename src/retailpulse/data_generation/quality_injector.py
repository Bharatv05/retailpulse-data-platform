# src/retailpulse/data_generation/quality_injector.py

import numpy  as np
import pandas as pd
from pathlib import Path
from datetime import timedelta

from retailpulse.data_generation.config  import (
    PRODUCT_CATALOG,
    RANDOM_SEED,
    CUSTOMERS_SOURCE_DIR,
    PRODUCTS_SOURCE_DIR,
    ORDERS_SOURCE_DIR,
    PAYMENTS_SOURCE_DIR,
    SHIPMENTS_SOURCE_DIR,
    MARKETING_SOURCE_DIR,
)
from retailpulse.data_generation.injector_config import (
    CAMPAIGN_CUSTOMER_INJECTION_RULES,
    CAMPAIGN_INJECTION_RULES,
    CUSTOMER_INJECTION_RULES,
    INVALID_CAMPAIGN_STATUSES,
    INVALID_ORDER_STATUSES,
    INVALID_PAYMENT_STATUSES,
    INVALID_SHIPMENT_STATUSES,
    INVALID_STATUS_VALUES,
    ORDER_INJECTION_RULES,
    ORDER_ITEM_INJECTION_RULES,
    PAYMENT_INJECTION_RULES,
    PRODUCT_INJECTION_RULES,
    SHIPMENT_INJECTION_RULES,
)

# ── RNG ────────────────────────────────────────────────────────────────────────

rng = np.random.default_rng(RANDOM_SEED + 99)   # different seed from generator


# ── Utility ────────────────────────────────────────────────────────────────────

def sample_indices(df: pd.DataFrame, rate: float) -> np.ndarray:
    """Return a random sample of row indices based on rate."""
    n = max(1, int(len(df) * rate))
    return rng.choice(df.index, size=n, replace=False)


def save_dirty(df: pd.DataFrame, clean_path: Path) -> None:
    """Save dirty version alongside the clean file."""
    dirty_path = clean_path.parent / clean_path.name.replace(".csv", "_dirty.csv")
    df.to_csv(dirty_path, index=False)
    print(f"   ✅ Dirty file saved → {dirty_path.name}  ({len(df):,} rows)")


def log_injection(problem: str, count: int) -> None:
    print(f"      ↳ {problem:<40} {count:>6} rows affected")


# ══════════════════════════════════════════════════════════════════════════════
# CUSTOMERS
# ══════════════════════════════════════════════════════════════════════════════

def inject_customers() -> None:
    print("\n── Customers ────────────────────────────────────────────")
    path = CUSTOMERS_SOURCE_DIR / "customers.csv"
    df   = pd.read_csv(path)

    # ── Cast columns that will receive mixed-type injections ──────────────────
    # phone is read as int64 from CSV.
    # We cast to str before injection so string-based bad values are accepted.
    df["phone"]      = df["phone"].astype(str)
    df["created_at"] = pd.to_datetime(df["created_at"])
    df["updated_at"] = pd.to_datetime(df["updated_at"])

    for rule in CUSTOMER_INJECTION_RULES:
        idx = sample_indices(df, rule["rate"])
        p   = rule["problem"]

        if p == "null_email":
            df.loc[idx, "email"] = None
            log_injection(p, len(idx))

        elif p == "invalid_email_format":
            invalid_emails = ["notanemail", "missing@", "@nodomain", "plaintext", "bad@@email.com"]
            df.loc[idx, "email"] = rng.choice(invalid_emails, size=len(idx))
            log_injection(p, len(idx))

        elif p == "duplicate_record":
            dupes = df.loc[
                rng.choice(df.index, size=max(1, int(len(df) * rule["rate"])), replace=False)
            ].copy()
            df = pd.concat([df, dupes], ignore_index=True)
            log_injection(p, len(dupes))

        elif p == "invalid_phone":
            invalid_phones = ["000", "ABCDE12345", "99999", "N/A", ""]
            df.loc[idx, "phone"] = rng.choice(invalid_phones, size=len(idx))
            log_injection(p, len(idx))

        elif p == "timestamp_reversal":
            df.loc[idx, "updated_at"] = (
                df.loc[idx, "created_at"]
                - pd.to_timedelta(rng.integers(1, 30, size=len(idx)), unit="D")
            )
            log_injection(p, len(idx))

    save_dirty(df, path)


# ══════════════════════════════════════════════════════════════════════════════
# PRODUCTS
# ══════════════════════════════════════════════════════════════════════════════

def inject_products() -> None:
    print("\n── Products ─────────────────────────────────────────────")
    path = PRODUCTS_SOURCE_DIR / "products.csv"
    df   = pd.read_csv(path)

    # Build a mismatched category/subcategory pool
    all_categories   = list(PRODUCT_CATALOG.keys())
    all_subcategories = [sub for subs in PRODUCT_CATALOG.values() for sub in subs]

    for rule in PRODUCT_INJECTION_RULES:
        idx = sample_indices(df, rule["rate"])
        p   = rule["problem"]

        if p == "null_unit_price":
            df.loc[idx, "unit_price"] = None
            log_injection(p, len(idx))

        elif p == "invalid_discount":
            bad_discounts = [-10.0, -5.0, 101.0, 150.0, 200.0]
            df.loc[idx, "discount_percentage"] = rng.choice(bad_discounts, size=len(idx))
            log_injection(p, len(idx))

        elif p == "invalid_category_combo":
            # Assign a subcategory that does NOT belong to the row's category
            for i in idx:
                current_cat = df.at[i, "category"]
                invalid_subs = [
                    s for cat, subs in PRODUCT_CATALOG.items()
                    if cat != current_cat
                    for s in subs
                ]
                df.at[i, "subcategory"] = str(rng.choice(invalid_subs))
            log_injection(p, len(idx))

        elif p == "duplicate_record":
            dupes = df.loc[rng.choice(df.index, size=max(1, int(len(df) * rule["rate"])), replace=False)]
            df    = pd.concat([df, dupes], ignore_index=True)
            log_injection(p, len(dupes))

        elif p == "invalid_status":
            df.loc[idx, "product_status"] = rng.choice(
                INVALID_STATUS_VALUES, size=len(idx)
            )
            log_injection(p, len(idx))

    save_dirty(df, path)


# ══════════════════════════════════════════════════════════════════════════════
# ORDERS
# ══════════════════════════════════════════════════════════════════════════════

def inject_orders() -> None:
    print("\n── Orders ───────────────────────────────────────────────")
    path = ORDERS_SOURCE_DIR / "orders.csv"
    df   = pd.read_csv(path)
    df["created_at"] = pd.to_datetime(df["created_at"])
    df["updated_at"] = pd.to_datetime(df["updated_at"])
    df["customer_id"] = df["customer_id"].astype(str)

    for rule in ORDER_INJECTION_RULES:
        idx = sample_indices(df, rule["rate"])
        p   = rule["problem"]

        if p == "null_customer_id":
            df.loc[idx, "customer_id"] = None
            log_injection(p, len(idx))

        elif p == "duplicate_record":
            dupes = df.loc[rng.choice(df.index, size=max(1, int(len(df) * rule["rate"])), replace=False)]
            df    = pd.concat([df, dupes], ignore_index=True)
            log_injection(p, len(dupes))

        elif p == "invalid_order_status":
            df.loc[idx, "order_status"] = rng.choice(
                INVALID_ORDER_STATUSES, size=len(idx)
            )
            log_injection(p, len(idx))

        elif p == "negative_total_amount":
            df.loc[idx, "total_amount"] = rng.uniform(-5000, 0, size=len(idx)).round(2)
            log_injection(p, len(idx))

        elif p == "timestamp_reversal":
            df.loc[idx, "updated_at"] = pd.to_datetime(
                df.loc[idx, "created_at"]
            ) - pd.to_timedelta(rng.integers(1, 30, size=len(idx)), unit="D")
            log_injection(p, len(idx))

    save_dirty(df, path)


# ══════════════════════════════════════════════════════════════════════════════
# ORDER ITEMS
# ══════════════════════════════════════════════════════════════════════════════

def inject_order_items() -> None:
    print("\n── Order Items ──────────────────────────────────────────")
    path = ORDERS_SOURCE_DIR / "order_items.csv"
    df   = pd.read_csv(path)
    df["product_id"] = df["product_id"].astype(str)
    df["order_id"]   = df["order_id"].astype(str)

    for rule in ORDER_ITEM_INJECTION_RULES:
        idx = sample_indices(df, rule["rate"])
        p   = rule["problem"]

        if p == "invalid_product_id":
            df.loc[idx, "product_id"] = [
                f"P{rng.integers(99000, 99999):06d}" for _ in range(len(idx))
            ]
            log_injection(p, len(idx))

        elif p == "invalid_order_id":
            df.loc[idx, "order_id"] = [
                f"O{rng.integers(9900000, 9999999):07d}" for _ in range(len(idx))
            ]
            log_injection(p, len(idx))

        elif p == "zero_negative_quantity":
            df.loc[idx, "quantity"] = rng.integers(-5, 1, size=len(idx))
            log_injection(p, len(idx))

        elif p == "incorrect_total_price":
            # Multiply total_price by a wrong factor to simulate calculation error
            df.loc[idx, "total_price"] = (
                df.loc[idx, "total_price"] * rng.uniform(1.5, 5.0, size=len(idx))
            ).round(2)
            log_injection(p, len(idx))

        elif p == "duplicate_record":
            dupes = df.loc[rng.choice(df.index, size=max(1, int(len(df) * rule["rate"])), replace=False)]
            df    = pd.concat([df, dupes], ignore_index=True)
            log_injection(p, len(dupes))

    save_dirty(df, path)


# ══════════════════════════════════════════════════════════════════════════════
# PAYMENTS
# ══════════════════════════════════════════════════════════════════════════════

def inject_payments() -> None:
    print("\n── Payments ─────────────────────────────────────────────")
    path = PAYMENTS_SOURCE_DIR / "payments.csv"
    df   = pd.read_csv(path)
    df["order_id"]        = df["order_id"].astype(str)
    df["payment_method"]  = df["payment_method"].astype(str)
    df["payment_status"]  = df["payment_status"].astype(str)

    for rule in PAYMENT_INJECTION_RULES:
        idx = sample_indices(df, rule["rate"])
        p   = rule["problem"]

        if p == "invalid_order_id":
            df.loc[idx, "order_id"] = [
                f"O{rng.integers(9900000, 9999999):07d}" for _ in range(len(idx))
            ]
            log_injection(p, len(idx))

        elif p == "amount_mismatch":
            # Alter payment amount by random factor — simulates partial/wrong payment recorded
            df.loc[idx, "payment_amount"] = (
                df.loc[idx, "payment_amount"] * rng.uniform(0.1, 0.8, size=len(idx))
            ).round(2)
            log_injection(p, len(idx))

        elif p == "invalid_payment_status":
            df.loc[idx, "payment_status"] = rng.choice(
                INVALID_PAYMENT_STATUSES, size=len(idx)
            )
            log_injection(p, len(idx))

        elif p == "duplicate_record":
            dupes = df.loc[rng.choice(df.index, size=max(1, int(len(df) * rule["rate"])), replace=False)]
            df    = pd.concat([df, dupes], ignore_index=True)
            log_injection(p, len(dupes))

        elif p == "null_payment_method":
            df.loc[idx, "payment_method"] = None
            log_injection(p, len(idx))

    save_dirty(df, path)


# ══════════════════════════════════════════════════════════════════════════════
# SHIPMENTS
# ══════════════════════════════════════════════════════════════════════════════

def inject_shipments() -> None:
    print("\n── Shipments ────────────────────────────────────────────")
    path = SHIPMENTS_SOURCE_DIR / "shipments.csv"
    df   = pd.read_csv(path, parse_dates=["shipment_date", "expected_delivery_date",
                                           "actual_delivery_date"])
    df["order_id"]        = df["order_id"].astype(str)
    df["shipment_status"] = df["shipment_status"].astype(str)

    for rule in SHIPMENT_INJECTION_RULES:
        idx = sample_indices(df, rule["rate"])
        p   = rule["problem"]

        if p == "invalid_order_id":
            df.loc[idx, "order_id"] = [
                f"O{rng.integers(9900000, 9999999):07d}" for _ in range(len(idx))
            ]
            log_injection(p, len(idx))

        elif p == "invalid_date_sequence":
            # Set shipment_date BEFORE order would allow it (simulate bad timestamps)
            df.loc[idx, "shipment_date"] = pd.to_datetime(
                df.loc[idx, "expected_delivery_date"]
            ) + pd.to_timedelta(rng.integers(1, 10, size=len(idx)), unit="D")
            log_injection(p, len(idx))

        elif p == "invalid_shipment_status":
            df.loc[idx, "shipment_status"] = rng.choice(
                INVALID_SHIPMENT_STATUSES, size=len(idx)
            )
            log_injection(p, len(idx))

        elif p == "missing_delivered_date":
            # Remove actual_delivery_date for DELIVERED shipments
            delivered_idx = df[df["shipment_status"] == "DELIVERED"].index
            if len(delivered_idx) > 0:
                target = rng.choice(
                    delivered_idx,
                    size=max(1, int(len(delivered_idx) * rule["rate"])),
                    replace=False,
                )
                df.loc[target, "actual_delivery_date"] = None
                log_injection(p, len(target))

    save_dirty(df, path)


# ══════════════════════════════════════════════════════════════════════════════
# CAMPAIGNS
# ══════════════════════════════════════════════════════════════════════════════

def inject_campaigns() -> None:
    print("\n── Campaigns ────────────────────────────────────────────")
    path = MARKETING_SOURCE_DIR / "campaigns.csv"
    df   = pd.read_csv(path, parse_dates=["start_date", "end_date"])
    df["campaign_status"] = df["campaign_status"].astype(str)

    for rule in CAMPAIGN_INJECTION_RULES:
        idx = sample_indices(df, rule["rate"])
        p   = rule["problem"]

        if p == "invalid_date_range":
            # Swap start and end so end_date < start_date
            for i in idx:
                df.at[i, "start_date"], df.at[i, "end_date"] = (
                    df.at[i, "end_date"],
                    df.at[i, "start_date"],
                )
            log_injection(p, len(idx))

        elif p == "invalid_budget":
            df.loc[idx, "budget"] = rng.uniform(-50000, 0, size=len(idx)).round(2)
            log_injection(p, len(idx))

        elif p == "invalid_status":
            df.loc[idx, "campaign_status"] = rng.choice(
                INVALID_CAMPAIGN_STATUSES, size=len(idx)
            )
            log_injection(p, len(idx))

        elif p == "duplicate_record":
            dupes = df.loc[rng.choice(df.index, size=max(1, int(len(df) * rule["rate"])), replace=False)]
            df    = pd.concat([df, dupes], ignore_index=True)
            log_injection(p, len(dupes))

    save_dirty(df, path)


# ══════════════════════════════════════════════════════════════════════════════
# CAMPAIGN CUSTOMERS
# ══════════════════════════════════════════════════════════════════════════════

def inject_campaign_customers() -> None:
    print("\n── Campaign Customers ───────────────────────────────────")
    path = MARKETING_SOURCE_DIR / "campaign_customers.csv"
    df   = pd.read_csv(path, parse_dates=["targeted_date", "conversion_date"])
    df["campaign_id"]  = df["campaign_id"].astype(str)
    df["customer_id"]  = df["customer_id"].astype(str)
    df["targeted_date"]   = pd.to_datetime(df["targeted_date"])
    df["conversion_date"] = pd.to_datetime(df["conversion_date"])

    for rule in CAMPAIGN_CUSTOMER_INJECTION_RULES:
        idx = sample_indices(df, rule["rate"])
        p   = rule["problem"]

        if p == "invalid_campaign_id":
            df.loc[idx, "campaign_id"] = [
                f"CAM{rng.integers(9000, 9999):04d}" for _ in range(len(idx))
            ]
            log_injection(p, len(idx))

        elif p == "invalid_customer_id":
            df.loc[idx, "customer_id"] = [
                f"C{rng.integers(900000, 999999):06d}" for _ in range(len(idx))
            ]
            log_injection(p, len(idx))

        elif p == "duplicate_pair":
            dupes = df.loc[rng.choice(df.index, size=max(1, int(len(df) * rule["rate"])), replace=False)]
            df    = pd.concat([df, dupes], ignore_index=True)
            log_injection(p, len(dupes))

        elif p == "invalid_conversion_date":
            # Set conversion_date BEFORE targeted_date
            converted_idx = df[df["converted"] == True].index
            if len(converted_idx) > 0:
                target = rng.choice(
                    converted_idx,
                    size=max(1, int(len(converted_idx) * rule["rate"])),
                    replace=False,
                )
                df.loc[target, "conversion_date"] = pd.to_datetime(
                    df.loc[target, "targeted_date"]
                ) - pd.to_timedelta(rng.integers(1, 10, size=len(target)), unit="D")
                log_injection(p, len(target))

        elif p == "false_converted_with_date":
            # converted = False but conversion_date is filled in
            not_converted_idx = df[df["converted"] == False].index
            if len(not_converted_idx) > 0:
                target = rng.choice(
                    not_converted_idx,
                    size=max(1, int(len(not_converted_idx) * rule["rate"])),
                    replace=False,
                )
                df.loc[target, "conversion_date"] = pd.to_datetime(
                    df.loc[target, "targeted_date"]
                ) + pd.to_timedelta(rng.integers(1, 10, size=len(target)), unit="D")
                log_injection(p, len(target))

    save_dirty(df, path)


# ══════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":

    print("=" * 60)
    print("  RETAILPULSE — QUALITY INJECTOR")
    print("  Injecting controlled impurities into source datasets")
    print("=" * 60)

    inject_customers()
    inject_products()
    inject_orders()
    inject_order_items()
    inject_payments()
    inject_shipments()
    inject_campaigns()
    inject_campaign_customers()

    print("\n" + "=" * 60)
    print("  INJECTION COMPLETE")
    print("  Dirty files written alongside clean source files.")
    print("  Bronze layer should read *_dirty.csv files.")
    print("=" * 60)