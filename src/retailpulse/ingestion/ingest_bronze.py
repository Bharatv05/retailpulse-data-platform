# src/retailpulse/ingestion/ingest_bronze.py

"""
Ingests dirty source CSVs into Bronze PostgreSQL tables.

Idempotency strategy:
  - Before inserting, check if source_file already exists in the table
  - If already loaded → skip entirely
  - If not loaded    → insert all rows
  - Same source file will never be loaded twice

NULL handling:
  - Empty strings and whitespace-only cells → converted to None → PostgreSQL NULL
  - Preserves injected NULLs from quality injector
"""

import uuid
from datetime import datetime
from pathlib import Path

import pandas as pd

from retailpulse.db_connection import get_db_connection
from retailpulse.ingestion.bronze_config import BRONZE_SCHEMA, SOURCE_FILE_MAP

# ── Project Root ───────────────────────────────────────────────────────────────

PROJECT_ROOT = Path(__file__).resolve().parents[3]
SOURCE_DIR   = PROJECT_ROOT / "data" / "source"


# ── Ingestion ID ───────────────────────────────────────────────────────────────

def generate_ingestion_id() -> str:
    """
    Unique ID for this pipeline run.
    Format: RUN_YYYYMMDD_HHMMSS_<short_uuid>
    Example: RUN_20240913_103215_a3f2
    """
    ts       = datetime.now().strftime("%Y%m%d_%H%M%S")
    short_id = str(uuid.uuid4())[:4]
    return f"RUN_{ts}_{short_id}"


# ── Idempotency Check ──────────────────────────────────────────────────────────

def is_already_loaded(conn, table_name: str, filename: str) -> bool:
    """
    Check if this source file has already been loaded into this Bronze table.

    Logic:
      SELECT COUNT(*) FROM bronze.<table> WHERE source_file = <filename>
      If count > 0 → already loaded → skip
      If count = 0 → not loaded    → proceed
    """
    query = f"""
        SELECT COUNT(*)
        FROM {BRONZE_SCHEMA}.{table_name}
        WHERE source_file = %s;
    """
    with conn.cursor() as cur:
        cur.execute(query, (filename,))
        count = cur.fetchone()[0]

    return count > 0


# ── NULL Normalisation ─────────────────────────────────────────────────────────

def normalise_nulls(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert empty strings and whitespace-only cells to Python None.
    None → psycopg → PostgreSQL NULL.

    Why:
      Pandas writes None as "" in CSV.
      Reading back with dtype=str keeps them as "".
      We must explicitly convert "" → None before insert.

    Regex ^\s*$ matches:
      ""     → empty string
      " "    → single space
      "   "  → multiple spaces
    """
    return df.replace(r'^\s*$', None, regex=True)


# ── Core Ingestion ─────────────────────────────────────────────────────────────

def ingest_table(
    conn         : object,
    table_name   : str,
    folder       : str,
    filename     : str,
    ingestion_id : str,
    ingested_at  : datetime,
) -> None:

    file_path = SOURCE_DIR / folder / filename

    if not file_path.exists():
        print(f"   ⚠️  File not found  : {file_path.name} — skipping")
        return

    # ── Idempotency gate ───────────────────────────────────────────────────────
    if is_already_loaded(conn, table_name, filename):
        print(f"   ⏭️  Already loaded  : bronze.{table_name:<25} "
              f"source: {filename} — skipping")
        return

    # ── Load CSV ───────────────────────────────────────────────────────────────
    df = pd.read_csv(file_path, dtype=str, keep_default_na=False)

    # ── Normalise NULLs ────────────────────────────────────────────────────────
    df = normalise_nulls(df)

    # ── Add audit columns ──────────────────────────────────────────────────────
    df["ingested_at"]  = ingested_at
    df["source_file"]  = filename
    df["ingestion_id"] = ingestion_id

    # ── Build INSERT statement ─────────────────────────────────────────────────
    columns      = list(df.columns)
    col_names    = ", ".join(columns)
    placeholders = ", ".join(["%s"] * len(columns))

    insert_sql = f"""
        INSERT INTO {BRONZE_SCHEMA}.{table_name} ({col_names})
        VALUES ({placeholders});
    """

    # ── Execute batch insert ───────────────────────────────────────────────────
    rows = [tuple(row) for row in df.itertuples(index=False, name=None)]

    with conn.cursor() as cur:
        cur.executemany(insert_sql, rows)

    conn.commit()

    print(f"   ✅ Loaded            : bronze.{table_name:<25} "
          f"{len(rows):>8,} rows  |  source: {filename}")


# ── Entry Point ────────────────────────────────────────────────────────────────

if __name__ == "__main__":

    ingestion_id = generate_ingestion_id()
    ingested_at  = datetime.now()

    print("=" * 65)
    print("  BRONZE INGESTION")
    print(f"  ingestion_id : {ingestion_id}")
    print(f"  ingested_at  : {ingested_at}")
    print("=" * 65)

    conn = get_db_connection()

    try:
        for table_name, (folder, filename) in SOURCE_FILE_MAP.items():
            ingest_table(
                conn         = conn,
                table_name   = table_name,
                folder       = folder,
                filename     = filename,
                ingestion_id = ingestion_id,
                ingested_at  = ingested_at,
            )
    finally:
        conn.close()

    print("\n" + "=" * 65)
    print("  BRONZE INGESTION COMPLETE")
    print(f"  ingestion_id : {ingestion_id}")
    print("=" * 65)