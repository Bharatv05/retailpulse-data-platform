# src/retailpulse/silver/create_silver.py

from retailpulse.db_connection import get_db_connection
from retailpulse.silver.silver_config import (
    ALL_CREATE_STATEMENTS,
    CREATE_SCHEMA,
    SILVER_SCHEMA,
)


def create_silver_schema(conn) -> None:
    with conn.cursor() as cur:
        cur.execute(CREATE_SCHEMA)
    conn.commit()
    print(f"✅ Schema '{SILVER_SCHEMA}' ready")


def create_silver_tables(conn) -> None:
    with conn.cursor() as cur:
        for statement in ALL_CREATE_STATEMENTS:
            cur.execute(statement)
    conn.commit()
    print(f"✅ All Silver tables created")


def verify_tables(conn) -> None:
    query = """
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = %s
        ORDER BY table_name;
    """
    with conn.cursor() as cur:
        cur.execute(query, (SILVER_SCHEMA,))
        tables = cur.fetchall()

    print(f"\n── Tables in '{SILVER_SCHEMA}' schema ──────────────")
    for (table,) in tables:
        print(f"   {SILVER_SCHEMA}.{table}")


if __name__ == "__main__":
    print("🔄 Setting up Silver layer...")
    print("=" * 50)
    conn = get_db_connection()
    try:
        create_silver_schema(conn)
        create_silver_tables(conn)
        verify_tables(conn)
    finally:
        conn.close()
    print("\n✅ Silver layer setup complete")