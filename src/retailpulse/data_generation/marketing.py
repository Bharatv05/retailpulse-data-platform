# src/retailpulse/data_generation/marketing.py

from datetime import datetime, timedelta

import numpy  as np
import pandas as pd

from retailpulse.data_generation.config import (
    CAMPAIGN_BUDGET_MAX,
    CAMPAIGN_BUDGET_MIN,
    CAMPAIGN_CHANNELS,
    CAMPAIGN_CHANNEL_WEIGHTS,
    CAMPAIGN_CONVERSION_RATE_MAX,
    CAMPAIGN_CONVERSION_RATE_MIN,
    CAMPAIGN_COUNT,
    CAMPAIGN_STATUSES,
    CAMPAIGN_STATUS_WEIGHTS,
    CAMPAIGN_TARGET_RATE_MAX,
    CAMPAIGN_TARGET_RATE_MIN,
    CUSTOMERS_SOURCE_DIR,
    MARKETING_SOURCE_DIR,
    RANDOM_SEED,
)

# ── ID Helpers ─────────────────────────────────────────────────────────────────

def generate_campaign_id(index: int) -> str:
    """CAM0001, CAM0002 ..."""
    return f"CAM{index:04d}"


def generate_bridge_id(index: int) -> str:
    """CC00000001, CC00000002 ..."""
    return f"CC{index:08d}"


# ── Campaign Name Builder ──────────────────────────────────────────────────────

# Realistic campaign name components
_CAMPAIGN_THEMES = [
    "Summer Sale", "Winter Fest", "Festive Offers",
    "Flash Sale", "New Arrivals", "Clearance Drive",
    "Champion Series", "Sports Day", "Back to School",
    "Weekend Special", "Loyalty Rewards", "Premium Collection",
]

_CAMPAIGN_TARGETS = [
    "Cricket Fans", "Football Lovers", "Running Enthusiasts",
    "Tennis Players", "Basketball Stars", "Sports Champions",
    "Active Lifestyle", "Team Players", "Fitness First",
]

def build_campaign_name(rng: np.random.Generator, channel: str) -> str:
    theme  = str(rng.choice(_CAMPAIGN_THEMES))
    target = str(rng.choice(_CAMPAIGN_TARGETS))
    return f"{theme} — {target}"


# ── Timestamp Helper ───────────────────────────────────────────────────────────

def generate_timestamps(
    base_date : datetime,
    rng       : np.random.Generator,
) -> tuple[datetime, datetime]:
    created_at = base_date
    updated_at = created_at + timedelta(hours=int(rng.integers(0, 25)))
    return created_at, updated_at


# ── Dependency Loader ──────────────────────────────────────────────────────────

def load_customer_ids() -> np.ndarray:
    path = CUSTOMERS_SOURCE_DIR / "customers.csv"
    df   = pd.read_csv(path, usecols=["customer_id"])
    return df["customer_id"].to_numpy()


# ── Campaign Generator ────────────────────────────────────────────────────────

def generate_campaigns(
    rng : np.random.Generator,
    n   : int = CAMPAIGN_COUNT,
) -> pd.DataFrame:
    """
    Generate the campaign master table.
    Grain: one row = one campaign.
    """

    # Campaign date range: 2022-01-01 to 2024-12-31
    # Campaigns run for 7 to 60 days
    start_boundary = datetime(2022, 1, 1)
    end_boundary   = datetime(2024, 12, 31)
    total_days     = (end_boundary - start_boundary).days

    records = []

    for i in range(1, n + 1):

        channel = str(rng.choice(CAMPAIGN_CHANNELS, p=CAMPAIGN_CHANNEL_WEIGHTS))

        # Campaign start and duration
        campaign_start    = start_boundary + timedelta(days=int(rng.integers(0, total_days - 60)))
        campaign_duration = int(rng.integers(7, 61))      # 7 to 60 days
        campaign_end      = campaign_start + timedelta(days=campaign_duration)

        budget = round(float(rng.uniform(CAMPAIGN_BUDGET_MIN, CAMPAIGN_BUDGET_MAX)), 2)

        status = str(rng.choice(CAMPAIGN_STATUSES, p=CAMPAIGN_STATUS_WEIGHTS))

        created_at, updated_at = generate_timestamps(campaign_start, rng)

        records.append({
            "campaign_id"    : generate_campaign_id(i),
            "campaign_name"  : build_campaign_name(rng, channel),
            "channel"        : channel,
            "start_date"     : campaign_start.date(),
            "end_date"       : campaign_end.date(),
            "budget"         : budget,
            "campaign_status": status,
            "created_at"     : created_at,
            "updated_at"     : updated_at,
        })

    return pd.DataFrame(records)


# ── Campaign Customers Generator ───────────────────────────────────────────────

def generate_campaign_customers(
    campaigns_df : pd.DataFrame,
    customer_ids : np.ndarray,
    rng          : np.random.Generator,
) -> pd.DataFrame:
    """
    Generate the bridge table.
    Grain: one row = one customer targeted by one campaign.

    For each campaign:
      1. Sample a random subset of customers (10% to 40%)
      2. Assign a targeted_date within the campaign window
      3. Randomly determine conversion (True/False)
      4. If converted → assign a conversion_date after targeted_date
    """

    records    = []
    bridge_idx = 1

    for _, campaign in campaigns_df.iterrows():

        campaign_id    = campaign["campaign_id"]
        campaign_start = pd.to_datetime(campaign["start_date"])
        campaign_end   = pd.to_datetime(campaign["end_date"])
        campaign_days  = (campaign_end - campaign_start).days

        # ── How many customers to target ───────────────────────────────────────
        target_rate  = rng.uniform(CAMPAIGN_TARGET_RATE_MIN, CAMPAIGN_TARGET_RATE_MAX)
        target_count = int(len(customer_ids) * target_rate)
        target_count = max(1, target_count)      # at least 1 customer

        # Sample WITHOUT replacement — a customer is targeted once per campaign
        targeted_customers = rng.choice(customer_ids, size=target_count, replace=False)

        # ── Conversion rate for this campaign ─────────────────────────────────
        conversion_rate = rng.uniform(CAMPAIGN_CONVERSION_RATE_MIN, CAMPAIGN_CONVERSION_RATE_MAX)

        for customer_id in targeted_customers:

            # Targeted on a random day within the campaign window
            targeted_date = campaign_start + timedelta(
                days=int(rng.integers(0, max(1, campaign_days)))
            )

            # Conversion decision
            converted = bool(rng.random() < conversion_rate)

            # Conversion date = targeted_date + 1 to 14 days
            if converted:
                conversion_date = targeted_date + timedelta(days=int(rng.integers(1, 15)))
                # Conversion cannot happen after campaign end + 7 days grace
                max_conversion  = campaign_end + timedelta(days=7)
                if conversion_date > max_conversion:
                    conversion_date = max_conversion
            else:
                conversion_date = None

            created_at, updated_at = generate_timestamps(targeted_date, rng)

            records.append({
                "id"              : generate_bridge_id(bridge_idx),
                "campaign_id"     : campaign_id,
                "customer_id"     : customer_id,
                "targeted_date"   : targeted_date.date(),
                "converted"       : converted,
                "conversion_date" : conversion_date.date() if conversion_date else None,
                "created_at"      : created_at,
                "updated_at"      : updated_at,
            })

            bridge_idx += 1

    return pd.DataFrame(records)


# ── Save ───────────────────────────────────────────────────────────────────────

def save_marketing(
    campaigns_df          : pd.DataFrame,
    campaign_customers_df : pd.DataFrame,
) -> None:

    MARKETING_SOURCE_DIR.mkdir(parents=True, exist_ok=True)

    campaigns_path          = MARKETING_SOURCE_DIR / "campaigns.csv"
    campaign_customers_path = MARKETING_SOURCE_DIR / "campaign_customers.csv"

    campaigns_df.to_csv(campaigns_path,                   index=False)
    campaign_customers_df.to_csv(campaign_customers_path, index=False)

    print(f"\n✅ Campaigns saved           → {campaigns_path}")
    print(f"   Rows written              : {len(campaigns_df):,}")
    print(f"\n✅ Campaign customers saved  → {campaign_customers_path}")
    print(f"   Rows written              : {len(campaign_customers_df):,}")

    # Summary stats
    total_targeted  = len(campaign_customers_df)
    total_converted = campaign_customers_df["converted"].sum()
    overall_rate    = (total_converted / total_targeted * 100) if total_targeted else 0

    print(f"\n   Total customers targeted  : {total_targeted:,}")
    print(f"   Total conversions         : {total_converted:,}")
    print(f"   Overall conversion rate   : {overall_rate:.1f}%")


# ── Entry Point ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("🔄 Generating marketing datasets...")

    rng          = np.random.default_rng(RANDOM_SEED)
    customer_ids = load_customer_ids()

    print(f"   Customers loaded          : {len(customer_ids):,}")
    print(f"   Campaigns to generate     : {CAMPAIGN_COUNT}")

    campaigns_df          = generate_campaigns(rng)
    campaign_customers_df = generate_campaign_customers(campaigns_df, customer_ids, rng)

    save_marketing(campaigns_df, campaign_customers_df)