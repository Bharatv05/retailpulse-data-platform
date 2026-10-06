# src/retailpulse/silver/silver_validators.py

"""
Reusable validation and casting functions for Silver processing.

Each function:
  - Accepts a single value (TEXT from Bronze)
  - Returns (cast_value, error_message)
  - If cast succeeds  → (value,  None)
  - If cast fails     → (None,   "reason string")
"""

import json
from datetime import datetime
from typing   import Any, Optional, Tuple

import pandas as pd


# ── Type: DATE ─────────────────────────────────────────────────────────────────

def cast_date(value: Any) -> Tuple[Optional[str], Optional[str]]:
    if value is None or value is pd.NaT:
        return None, None
    try:
        if pd.isna(value):
            return None, None
    except (ValueError, TypeError):
        pass
    try:
        return pd.to_datetime(value).date(), None
    except Exception:
        return None, f"Cannot cast '{value}' to DATE"


# ── Type: TIMESTAMP ────────────────────────────────────────────────────────────

def cast_timestamp(value: Any) -> Tuple[Optional[datetime], Optional[str]]:
    if value is None or value is pd.NaT:
        return None, None
    try:
        if pd.isna(value):
            return None, None
    except (ValueError, TypeError):
        pass
    try:
        return pd.to_datetime(value), None
    except Exception:
        return None, f"Cannot cast '{value}' to TIMESTAMP"


# ── Type: NUMERIC ──────────────────────────────────────────────────────────────

def cast_numeric(value: Any) -> Tuple[Optional[float], Optional[str]]:
    if value is None or value is pd.NaT:
        return None, None
    try:
        if pd.isna(value):
            return None, None
    except (ValueError, TypeError):
        pass
    try:
        return float(value), None
    except Exception:
        return None, f"Cannot cast '{value}' to NUMERIC"


# ── Type: INTEGER ──────────────────────────────────────────────────────────────

def cast_integer(value: Any) -> Tuple[Optional[int], Optional[str]]:
    if value is None or value is pd.NaT:
        return None, None
    try:
        if pd.isna(value):
            return None, None
    except (ValueError, TypeError):
        pass
    try:
        return int(float(value)), None
    except Exception:
        return None, f"Cannot cast '{value}' to INTEGER"


# ── Type: BOOLEAN ──────────────────────────────────────────────────────────────

def cast_boolean(value: Any) -> Tuple[Optional[bool], Optional[str]]:
    if value is None or value is pd.NaT:
        return None, None
    try:
        if pd.isna(value):
            return None, None
    except (ValueError, TypeError):
        pass
    if isinstance(value, bool):
        return value, None
    if str(value).strip().lower() in {"true", "1", "yes"}:
        return True, None
    if str(value).strip().lower() in {"false", "0", "no"}:
        return False, None
    return None, f"Cannot cast '{value}' to BOOLEAN"


# ── Text ────────────────────────────────────────────────────────────────────

def cast_text(value: Any) -> Tuple[Optional[str], Optional[str]]:
    if value is None or value is pd.NaT:
        return None, None
    try:
        if pd.isna(value):
            return None, None
    except (ValueError, TypeError):
        pass
    return str(value).strip(), None


# ── NULL check ─────────────────────────────────────────────────────────────

def check_not_null(value: Any, column_name: str) -> Optional[str]:
    if value is None or value is pd.NaT:
        return f"Critical column '{column_name}' is NULL"
    try:
        if pd.isna(value):
            return f"Critical column '{column_name}' is NULL"
    except (ValueError, TypeError):
        pass
    return None

# ── Safe date comparison ───────────────────────────────────────────────────────

def safe_date_before(date_a, date_b) -> bool:
    """
    Returns True if date_a < date_b.
    Returns False if either is None or NaT.

    Usage:
      if safe_date_before(conversion_date, targeted_date):
          errors.append("conversion before targeting")

    Why:
      NaT < datetime.date → TypeError
      None < datetime.date → TypeError in some Python versions
      This function handles both safely.
    """
    if date_a is None or date_b is None:
        return False
    if date_a is pd.NaT or date_b is pd.NaT:
        return False
    try:
        return date_a < date_b
    except TypeError:
        return False

# ── Domain value check ─────────────────────────────────────────────────────────

def check_domain(
    value      : Any,
    valid_values: set,
    column_name : str,
) -> Optional[str]:
    """
    Returns error string if value is not in valid_values.
    Returns None if valid.
    Skips check if value is NULL (NULL check is separate).
    """
    if value is None:
        return None
    if value not in valid_values:
        return f"'{value}' is not a valid {column_name}"
    return None


# ── Record serialiser for quarantine ──────────────────────────────────────────

def serialise_record(row: dict) -> str:
    """Convert a row dict to JSON string for storage in rejected_records."""
    return json.dumps(
        {k: str(v) if v is not None else None for k, v in row.items()},
        default=str,
    )