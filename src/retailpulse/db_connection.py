"""
Central database connection module.

Provides get_db_connection() which returns an open psycopg connection.
The caller is responsible for closing the connection.

Usage:
    conn = get_db_connection()
    try:
        # use conn
    finally:
        conn.close()

Or as context manager:
    with get_db_connection() as conn:
        # use conn
"""

import psycopg
from psycopg import errors

from retailpulse.config import (
    POSTGRES_DB,
    POSTGRES_HOST,
    POSTGRES_PASSWORD,
    POSTGRES_PORT,
    POSTGRES_USER,
)


def get_db_connection() -> psycopg.Connection:
    """
    Opens and returns a PostgreSQL connection.

    Raises a clear error message if connection fails.
    Does NOT silently swallow exceptions —
    ingestion scripts need to know when DB is unavailable.
    """
    try:
        conn = psycopg.connect(
            host     = POSTGRES_HOST,
            port     = POSTGRES_PORT,
            dbname   = POSTGRES_DB,
            user     = POSTGRES_USER,
            password = POSTGRES_PASSWORD,
        )
        return conn

    except errors.OperationalError as err:
        raise ConnectionError(
            f"❌ Cannot connect to PostgreSQL.\n"
            f"   Check that PostgreSQL is running.\n"
            f"   Details: {err}"
        )

    except errors.InvalidPassword as err:
        raise ConnectionError(
            f"❌ Authentication failed.\n"
            f"   Check POSTGRES_USER and POSTGRES_PASSWORD in .env\n"
            f"   Details: {err}"
        )

    except errors.InvalidCatalogName as err:
        raise ConnectionError(
            f"❌ Database does not exist.\n"
            f"   Check POSTGRES_DB in .env — "
            f"   make sure '{POSTGRES_DB}' has been created.\n"
            f"   Details: {err}"
        )

    except psycopg.Error as err:
        raise ConnectionError(
            f"❌ Unexpected PostgreSQL error.\n"
            f"   Details: {err}"
        )


def test_connection() -> None:
    """
    Quick sanity check — connects, runs SELECT version(), closes.
    Used for manual verification only.
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT version();")
            version = cur.fetchone()[0]
        print(f"✅ Connection successful")
        print(f"   {version}")
    finally:
        conn.close()


if __name__ == "__main__":
    test_connection()