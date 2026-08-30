import psycopg
from psycopg import errors
print("Test")
from retailpulse.config import (
    POSTGRES_DB,
    POSTGRES_HOST,
    POSTGRES_PASSWORD,
    POSTGRES_PORT,
    POSTGRES_USER
)


def db_connector() -> None:
    
    try:
        connection = psycopg.connect(
                host = POSTGRES_HOST,
                port = POSTGRES_PORT,
                dbname = POSTGRES_DB,
                user = POSTGRES_USER,
                password = POSTGRES_PASSWORD,
            )

        with connection.cursor() as cursor:
            cursor.execute("SELECT version();")
            result = cursor.fetchone()

            print("PostgreSQL Connection Successful.")
            print(result[0])

    # == OPERATION ERRORS ==
    except errors.OperationalError as err: # type: ignore
        print(f"Network or Server Error: Check if Postgres is running. Details: {err}")

    # == Invalid Password ERRORS ==
    except errors.InvalidPassword as err: # type: ignore
        print(f"Auth Error: Check your database password. Details: {err}")

    # 3. Handle a missing database name
    except errors.InvalidCatalogName as err: # type: ignore
        print(f"Database Error: The database name does not exist. Details: {err}")

    # 4. Handle a missing table name
    except errors.UndefinedTable as err: # type: ignore
        print(f"SQL Error: The table you are querying does not exist. Details: {err}")

    # 5. Catchall for any other PostgreSQL-specific issue
    except psycopg.Error as err:
        print(f"General Postgres Error occurred: {err}")

    finally:
        print("==== DB CONNECTIVITY AND HEALTH CHECK RUNS ====")

if __name__ == "__main__":
    db_connector()