import os
from dotenv import  load_dotenv

load_dotenv()

APP_ENV = os.getenv("APP_ENV", "development")

POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", "5432"))
POSTGRES_DB = os.getenv("POSTGRES_DB", "retailpulse")
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")


if not POSTGRES_PASSWORD:
    raise ValueError("POSTGRES_PASSWORD is not configured")