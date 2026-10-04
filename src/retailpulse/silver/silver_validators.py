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


# ── Type: TEXT passthrough ─────────────────────────────────────────────────────

def cast_text(value: Any) -> Tuple[Optional[str], Optional[str]]:
    if pd.isna(value) or value is None:
        return None, None
    return str(value).strip(), None


# ── Type: DATE ─────────────────────────────────────────────────────────────────

def cast_date(value: Any) -> Tuple[Optional[str], Optional[str]]:
    if pd.isna(value) or value is None:
        return None, None
    try:
        return pd.to_datetime(value).date(), None
    except Exception:
        return None, f"Cannot cast '{value}' to DATE"


# ── Type: TIMESTAMP ────────────────────────────────────────────────────────────

def cast_timestamp(value: Any) -> Tuple[Optional[datetime], Optional[str]]:
    if pd.isna(value) or value is None:
        return None, None
    try:
        return pd.to_datetime(value), None
    except Exception:
        return None, f"Cannot cast '{value}' to TIMESTAMP"


# ── Type: NUMERIC ──────────────────────────────────────────────────────────────

def cast_numeric(value: Any) -> Tuple[Optional[float], Optional[str]]:
    if pd.isna(value) or value is None:
        return None, None
    try:
        return float(value), None
    except Exception:
        return None, f"Cannot cast '{value}' to NUMERIC"


# ── Type: INTEGER ──────────────────────────────────────────────────────────────

def cast_integer(value: Any) -> Tuple[Optional[int], Optional[str]]:
    if pd.isna(value) or value is None:
        return None, None
    try:
        return int(float(value)), None
    except Exception:
        return None, f"Cannot cast '{value}' to INTEGER"


# ── Type: BOOLEAN ──────────────────────────────────────────────────────────────

def cast_boolean(value: Any) -> Tuple[Optional[bool], Optional[str]]:
    if pd.isna(value) or value is None:
        return None, None
    if isinstance(value, bool):
        return value, None
    if str(value).strip().lower() in {"true", "1", "yes"}:
        return True, None
    if str(value).strip().lower() in {"false", "0", "no"}:
        return False, None
    return None, f"Cannot cast '{value}' to BOOLEAN"


# ── NULL check on critical column ──────────────────────────────────────────────

def check_not_null(value: Any, column_name: str) -> Optional[str]:
    """
    Returns error string if value is NULL.
    Returns None if value is present (no error).
    """
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return f"Critical column '{column_name}' is NULL"
    return None


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