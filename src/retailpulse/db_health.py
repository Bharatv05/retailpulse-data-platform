# src/retailpulse/db_health.py

"""
Database health check.
Uses get_db_connection() from db_connection module.
Run this to verify PostgreSQL is reachable before running any pipeline.
"""

from retailpulse.db_connection import get_db_connection


def db_connector() -> None:
    try:
        conn = get_db_connection()

        with conn.cursor() as cursor:
            cursor.execute("SELECT version();")
            result = cursor.fetchone()

        print("✅ PostgreSQL Connection Successful.")
        print(f"   {result[0]}")

    except ConnectionError as err:
        print(err)

    finally:
        print("\n==== DB CONNECTIVITY AND HEALTH CHECK COMPLETE ====")

        try:
            conn.close()
        except Exception:
            pass


if __name__ == "__main__":
    db_connector()