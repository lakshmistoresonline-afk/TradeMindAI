"""
================================================================================
TradeMindAI: Non-Destructive Local Database Layer
================================================================================
Dynamic database connection engine with automatic retry logic, query optimization,
and non-destructive table management for 100% offline local operation.
"""

import os
import time
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import OperationalError

logger = logging.getLogger(__name__)

# Dynamic Database URL Resolution (Detects local PostgreSQL or SQLite trade_mind.db)
LOCAL_DB_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DEFAULT_SQLITE_PATH = os.path.join(LOCAL_DB_DIR, "trade_mind.db")

DATABASE_URL = os.getenv(
    "LOCAL_DATABASE_URL",
    os.getenv("DATABASE_URL", f"sqlite:///{DEFAULT_SQLITE_PATH}")
)

# Engine Configuration
is_sqlite = "sqlite" in DATABASE_URL.lower()

engine_kwargs = {
    "echo": False,
}

if is_sqlite:
    engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    engine_kwargs.update({
        "pool_size": 20,
        "max_overflow": 10,
        "pool_pre_ping": True,
        "pool_recycle": 300,
    })

def create_db_engine_with_retry(retries: int = 3, delay: int = 2):
    """
    Establishes database connection with automatic retry logic for local resilience.
    """
    for attempt in range(1, retries + 1):
        try:
            engine = create_engine(DATABASE_URL, **engine_kwargs)
            # Test connection
            with engine.connect() as conn:
                pass
            logger.info(f"[Local DB] Connected successfully to {DATABASE_URL}")
            return engine
        except OperationalError as err:
            logger.warning(f"[Local DB] Connection attempt {attempt}/{retries} failed: {err}")
            if attempt < retries:
                time.sleep(delay)
            else:
                logger.error("[Local DB] Max connection retries reached. Falling back to SQLite.")
                fallback_url = f"sqlite:///{DEFAULT_SQLITE_PATH}"
                return create_engine(fallback_url, connect_args={"check_same_thread": False})

engine = create_db_engine_with_retry()

from sqlalchemy import event

@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """
    Enables SQLite Write-Ahead Logging (WAL) mode to eliminate "database is locked" errors
    during concurrent local read/write operations.
    """
    if "sqlite" in DATABASE_URL.lower():
        try:
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA journal_mode=WAL;")
            cursor.execute("PRAGMA synchronous=NORMAL;")
            cursor.close()
        except Exception as e:
            logger.warning(f"[Local DB] WAL PRAGMA setup notice: {e}")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """
    FastAPI Dependency for database session lifecycle management.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
