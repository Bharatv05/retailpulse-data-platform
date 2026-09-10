# src/retailpulse/data_generation/marketing_verification.py

from pathlib import Path
import pandas as pd

# ── Load Data ──────────────────────────────────────────────────────────────────

PROJECT_ROOT = Path(__file__).resolve().parents[3]
SOURCE_DIR = PROJECT_ROOT / "data" / "source"

campaigns_df = pd.read_csv(
    SOURCE_DIR / "marketing" / "campaigns.csv",
    parse_dates=["start_date", "end_date"],
)
cc_df = pd.read_csv(
    SOURCE_DIR / "marketing" / "campaign_customers.csv",
    parse_dates=["targeted_date", "conversion_date"],
)
customers_df = pd.read_csv(SOURCE_DIR / "customers" / "customers.csv")

campaigns_df["created_at"] = pd.to_datetime(campaigns_df["created_at"])
campaigns_df["updated_at"] = pd.to_datetime(campaigns_df["updated_at"])
cc_df["created_at"] = pd.to_datetime(cc_df["created_at"])
cc_df["updated_at"] = pd.to_datetime(cc_df["updated_at"])

print("=" * 60)
print("  MARKETING VERIFICATION")
print("=" * 60)

# ══════════════════════════════════════════════════════════════
# SECTION 1 — BASIC COUNTS  (provided)
# ══════════════════════════════════════════════════════════════

print("\n── Section 1: Basic Counts ──────────────────────────────")
print(f"Campaigns                  : {len(campaigns_df):,}")
print(f"Campaign customer rows     : {len(cc_df):,}")
print(f"Avg customers per campaign : {len(cc_df)/len(campaigns_df):,.0f}")

# ══════════════════════════════════════════════════════════════
# SECTION 2 — UNIQUENESS  (provided)
# ══════════════════════════════════════════════════════════════

print("\n── Section 2: Uniqueness ────────────────────────────────")
print(f"Unique campaign_ids        : {campaigns_df['campaign_id'].is_unique}")
print(
    f"Duplicate campaign_ids     : {campaigns_df['campaign_id'].duplicated().sum()}"
)
print(f"Unique bridge ids          : {cc_df['id'].is_unique}")
print(f"Duplicate bridge ids       : {cc_df['id'].duplicated().sum()}")

# ══════════════════════════════════════════════════════════════
# SECTION 3 — NULL CHECKS  (provided)
# ══════════════════════════════════════════════════════════════

print("\n── Section 3: NULL Checks ───────────────────────────────")
print("Campaigns NULLs:")
print(campaigns_df.isnull().sum())
print("\nCampaign customers NULLs:")
print(cc_df.isnull().sum())

# ══════════════════════════════════════════════════════════════
# SECTION 4 — REFERENTIAL INTEGRITY
# ══════════════════════════════════════════════════════════════

print("\n── Section 4: Referential Integrity ─────────────────────")

# ✅ PROVIDED — All campaign_ids in bridge table must exist in campaigns
valid_campaign_ids = set(campaigns_df["campaign_id"])
bridge_campaign_ids = set(cc_df["campaign_id"])
print(
    f"Campaign IDs not in master : {len(bridge_campaign_ids - valid_campaign_ids)}"
)

# 🔨 TASK 4A ───────────────────────────────────────────────────
# All customer_ids in campaign_customers must exist in customers.csv
#
# Hint:
#   - Get set of customer_ids from customers_df
#   - Get set of customer_ids from cc_df
#   - Find IDs in cc_df that are NOT in customers
#   - Expected result: 0
#
# YOUR CODE BELOW:
valid_customer_ids = set(customers_df["customer_id"])
cc_customer_ids = set(cc_df["customer_id"])
missing_customers = cc_customer_ids - valid_customer_ids
print(f"Customer IDs not in master : {len(missing_customers)}")

# 🔨 TASK 4B ───────────────────────────────────────────────────
# Each customer should appear at most ONCE per campaign.
# (A customer cannot be targeted twice by the same campaign.)
#
# Hint:
#   - Group cc_df by ["campaign_id", "customer_id"]
#   - Count occurrences
#   - Any count > 1 is a violation
#   - Expected result: 0
#
# YOUR CODE BELOW:
duplicate_targets = cc_df.duplicated(
    subset=["campaign_id", "customer_id"]
).sum()
print(f"Duplicate customer targets : {duplicate_targets}")

# ══════════════════════════════════════════════════════════════
# SECTION 5 — BUSINESS RULE CHECKS
# ══════════════════════════════════════════════════════════════

print("\n── Section 5: Business Rules ────────────────────────────")

# ✅ PROVIDED — Valid channels
valid_channels = {"EMAIL", "SMS", "SOCIAL_MEDIA", "PUSH_NOTIFICATION"}
print(
    f"Invalid channels           : "
    f"{(~campaigns_df['channel'].isin(valid_channels)).sum()}"
)

# ✅ PROVIDED — Valid statuses
valid_statuses = {"ACTIVE", "COMPLETED", "PAUSED"}
print(
    f"Invalid statuses           : "
    f"{(~campaigns_df['campaign_status'].isin(valid_statuses)).sum()}"
)

# ✅ PROVIDED — Budget always positive
print(f"Zero/negative budget       : {(campaigns_df['budget'] <= 0).sum()}")

# 🔨 TASK 5A ───────────────────────────────────────────────────
# Converted customers must have a conversion_date (not NULL).
# Non-converted customers must have conversion_date = NULL.
#
# Part 1: converted = True but conversion_date is NULL
# Part 2: converted = False but conversion_date is NOT NULL
#
# Expected result for both: 0
#
# YOUR CODE BELOW:
converted_null_date = (
    (cc_df["converted"] == True) & (cc_df["conversion_date"].isna())
).sum()
not_converted_with_date = (
    (cc_df["converted"] == False) & (cc_df["conversion_date"].notna())
).sum()
print(f"Converted with NULL date   : {converted_null_date}")
print(f"Not converted with date    : {not_converted_with_date}")

# 🔨 TASK 5B ───────────────────────────────────────────────────
# conversion_date must always be AFTER targeted_date.
# A customer cannot convert before being targeted.
#
# Hint:
#   - Filter rows where converted = True
#   - Compare conversion_date vs targeted_date
#   - Expected result: 0
#
# YOUR CODE BELOW:
converted_records = cc_df[cc_df["converted"] == True]
conv_before_target = (
    converted_records["conversion_date"] < converted_records["targeted_date"]
).sum()
print(f"Conversion before target   : {conv_before_target}")

# ══════════════════════════════════════════════════════════════
# SECTION 6 — DATE LOGIC CHECKS
# ══════════════════════════════════════════════════════════════

print("\n── Section 6: Date Logic ────────────────────────────────")

# 🔨 TASK 6A ───────────────────────────────────────────────────
# end_date must always be after start_date for every campaign.
# A campaign cannot end before it starts.
#
# Hint:
#   - Compare campaigns_df["end_date"] vs campaigns_df["start_date"]
#   - Expected result: 0
#
# YOUR CODE BELOW:
invalid_campaign_dates = (
    campaigns_df["end_date"] < campaigns_df["start_date"]
).sum()
print(f"Campaign end < start       : {invalid_campaign_dates}")

# 🔨 TASK 6B ───────────────────────────────────────────────────
# targeted_date must fall within the campaign window.
# (targeted_date >= start_date AND targeted_date <= end_date)
#
# Hint:
#   - Merge cc_df with campaigns_df on campaign_id
#   - Check targeted_date is within [start_date, end_date]
#   - Expected result: 0
#
# YOUR CODE BELOW:
merged_cc = cc_df.merge(
    campaigns_df[["campaign_id", "start_date", "end_date"]],
    on="campaign_id",
    how="inner",
)
outside_window = (
    (merged_cc["targeted_date"] < merged_cc["start_date"])
    | (merged_cc["targeted_date"] > merged_cc["end_date"])
).sum()
print(f"Target outside window      : {outside_window}")

# ══════════════════════════════════════════════════════════════
# SECTION 7 — TIMESTAMP VALIDITY  (provided)
# ══════════════════════════════════════════════════════════════

print("\n── Section 7: Timestamps ────────────────────────────────")
print(
    f"Campaigns updated < created    : "
    f"{(campaigns_df['updated_at'] < campaigns_df['created_at']).sum()}"
)
print(
    f"CC updated < created           : "
    f"{(cc_df['updated_at'] < cc_df['created_at']).sum()}"
)

# ══════════════════════════════════════════════════════════════
# SECTION 8 — DISTRIBUTION SUMMARY  (provided)
# ══════════════════════════════════════════════════════════════

print("\n── Section 8: Distributions ─────────────────────────────")

print("\nChannel distribution:")
print(campaigns_df["channel"].value_counts())

print("\nCampaign status distribution:")
print(campaigns_df["campaign_status"].value_counts())

print("\nConversion summary:")
total = len(cc_df)
converted = cc_df["converted"].sum()
print(f"  Total targeted            : {total:,}")
print(f"  Total converted           : {converted:,}")
print(f"  Overall conversion rate   : {converted/total*100:.1f}%")

print("\nConversions per campaign (top 5):")
print(
    cc_df.groupby("campaign_id")["converted"]
    .sum()
    .sort_values(ascending=False)
    .head(5)
)