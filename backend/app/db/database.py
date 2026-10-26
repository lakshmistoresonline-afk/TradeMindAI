"""
================================================================================
TradeMindAI: Non-Destructive Local Database Layer (Hardened & Sanitized)
================================================================================
Dynamic database connection engine with automatic retry logic, query optimization,
and non-destructive table management for offline local operation with strict
fail-closed production validation and credential redaction.
"""

import os
import time
import logging
from urllib.parse import urlparse, urlunparse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import OperationalError

logger = logging.getLogger(__name__)

def sanitize_db_url(url: str | None) -> str:
    if not url:
        return "<EMPTY>"
    try:
        parsed = urlparse(url)
        if parsed.password:
            user = parsed.username or ""
            host = parsed.hostname or ""
            port = f":{parsed.port}" if parsed.port else ""
            netloc = f"{user}:***@{host}{port}"
            parsed = parsed._replace(netloc=netloc)
        return urlunparse(parsed)
    except Exception:
        return "<REDACTED_URL>"

LOCAL_DB_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DEFAULT_SQLITE_PATH = os.path.join(LOCAL_DB_DIR, "trade_mind.db")

db_url_env = os.getenv("POSTGRES_URL")
db_url_alt = os.getenv("DATABASE_URL")
local_db_env = os.getenv("LOCAL_DATABASE_URL")

if db_url_env and db_url_alt and db_url_env.strip() != db_url_alt.strip():
    raise ValueError(
        f"CRITICAL SECURITY AUDIT FAILURE: Conflicting database URLs detected between POSTGRES_URL ({sanitize_db_url(db_url_env)}) "
        f"and DATABASE_URL ({sanitize_db_url(db_url_alt)})."
    )

DATABASE_URL = local_db_env or db_url_env or db_url_alt

is_railway = os.getenv("RAILWAY_ENVIRONMENT") is not None
is_production = is_railway or os.getenv("ENVIRONMENT", "").lower() == "production"

if is_production:
    if not DATABASE_URL:
        raise ValueError("CRITICAL SECURITY AUDIT FAILURE: Production environment requires a valid PostgreSQL URL. None provided.")
    if "sqlite" in DATABASE_URL.lower():
        raise ValueError(f"CRITICAL SECURITY AUDIT FAILURE: SQLite is strictly prohibited in production environments (got {sanitize_db_url(DATABASE_URL)}).")
else:
    if not DATABASE_URL or "sqlite" in DATABASE_URL.lower():
        DATABASE_URL = f"sqlite:///{DEFAULT_SQLITE_PATH}"

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
        "connect_args": {"connect_timeout": 10}
    })

def create_db_engine_with_retry(retries: int = 3, delay: int = 2):
    for attempt in range(1, retries + 1):
        try:
            engine = create_engine(DATABASE_URL, **engine_kwargs)
            with engine.connect() as conn:
                pass
            logger.info(f"[Local DB] Connected successfully to {sanitize_db_url(DATABASE_URL)}")
            return engine
        except OperationalError as err:
            logger.warning(f"[Local DB] Connection attempt {attempt}/{retries} failed on {sanitize_db_url(DATABASE_URL)}: {err}")
            if attempt < retries:
                time.sleep(delay)
            else:
                if is_production:
                    logger.error(f"[CRITICAL] Production database connection failed after retries on {sanitize_db_url(DATABASE_URL)}. Fail-closed enforced.")
                    raise ConnectionError(f"CRITICAL PRODUCTION FAILURE: Exhausted database connection retries. SQLite fallback prohibited in production.")
                else:
                    logger.error("[Local DB] Max connection retries reached. Falling back to SQLite.")
                    fallback_url = f"sqlite:///{DEFAULT_SQLITE_PATH}"
                    return create_engine(fallback_url, connect_args={"check_same_thread": False})

engine = create_db_engine_with_retry()

from sqlalchemy import event

@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
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
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
