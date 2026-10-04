# src/retailpulse/ingestion/create_bronze.py

"""
Creates the Bronze schema and all Bronze tables in PostgreSQL.
Safe to run multiple times — uses CREATE IF NOT EXISTS.
"""

import psycopg2
from retailpulse.db_connection import get_db_connection
from retailpulse.ingestion.bronze_config import (
    ALL_CREATE_STATEMENTS,
    BRONZE_SCHEMA,
    CREATE_SCHEMA,
    SOURCE_FILE_MAP,
)


def create_bronze_schema(conn) -> None:
    with conn.cursor() as cur:
        cur.execute(CREATE_SCHEMA)
    conn.commit()
    print(f"✅ Schema '{BRONZE_SCHEMA}' ready")


def create_bronze_tables(conn) -> None:
    with conn.cursor() as cur:
        for statement in ALL_CREATE_STATEMENTS:
            cur.execute(statement)
    conn.commit()
    print(f"✅ All Bronze tables created")


def verify_tables(conn) -> None:
    """List all tables created in the bronze schema."""
    query = """
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = %s
        ORDER BY table_name;
    """
    with conn.cursor() as cur:
        cur.execute(query, (BRONZE_SCHEMA,))
        tables = cur.fetchall()

    print(f"\n── Tables in '{BRONZE_SCHEMA}' schema ──────────────────")
    for (table,) in tables:
        print(f"   {BRONZE_SCHEMA}.{table}")


if __name__ == "__main__":
    print("🔄 Setting up Bronze layer...")
    print("=" * 50)

    conn = get_db_connection()

    try:
        create_bronze_schema(conn)
        create_bronze_tables(conn)
        verify_tables(conn)
    finally:
        conn.close()

    print("\n✅ Bronze layer setup complete")