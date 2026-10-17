"""
================================================================================
TradeMindAI: Local Offline FastAPI Application Entry Point
================================================================================
100% Offline Local Operation Application Server.
Incorporates modular routers and non-destructive database auto-seeding on startup.
"""

import logging
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from backend.app.db.database import Base, engine
from backend.app.db.seed import seed_local_database
from backend.app.api import health, ticker, indicators, signals, import_data
from backend.api.v1.api import api_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TradeMindAI")

app = FastAPI(
    title="TradeMindAI Local Offline API",
    version="2.3.0-LOCAL",
    description="100% Offline Local Quantitative Signal & TA Engine"
)

# Enable CORS with explicit authorized origins (no wildcard with credentials in any environment)
allowed_origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://localhost:8000",
    "https://com-webcraft-trademindai-c8f75.web.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
)

# Include Canonical V1 API Router and Modular Local Routers
app.include_router(api_router, prefix="/api/v1")
app.include_router(health.router)
app.include_router(ticker.router)
app.include_router(indicators.router)
app.include_router(signals.router)
app.include_router(import_data.router)

from backend.core.postgres import Base as PostgresBase, engine as postgres_engine

def ensure_sqlite_columns(eng=None):
    """
    Idempotent and independent SQLite column migration for live_signals and shadow_signals.
    Inspects each required target price column independently and adds missing ones.
    Fails safely on error instead of silently swallowing.
    """
    target_engine = eng if eng is not None else postgres_engine
    engine_url_str = str(target_engine.url).lower()
    if "sqlite" not in engine_url_str:
        logger.info("[Migration] Non-SQLite engine detected (%s). Skipping SQLite migration.", engine_url_str)
        return

    try:
        with target_engine.connect() as conn:
            from sqlalchemy import text
            for table_name in ["live_signals", "shadow_signals"]:
                tables = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name=:t"), {"t": table_name}).fetchall()
                if not tables:
                    logger.info("[Migration] %s table does not exist yet. Skipping column checks.", table_name)
                    continue

                res = conn.execute(text(f"PRAGMA table_info({table_name})")).fetchall()
                existing_cols = [row[1] for row in res]
                logger.info("[Migration] Existing columns in %s: %s", table_name, existing_cols)

                required_cols = ["target_price_1", "target_price_2", "target_price_3"]
                missing_cols = [col for col in required_cols if col not in existing_cols]

                if missing_cols:
                    logger.info("[Migration] Missing columns detected in %s: %s. Adding...", table_name, missing_cols)
                    for col in missing_cols:
                        conn.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {col} FLOAT"))
                    conn.commit()
                    logger.info("[Migration] Successfully added missing columns to %s.", table_name)
                else:
                    logger.info("[Migration] All target price columns already exist in %s.", table_name)
    except Exception as e:
        logger.exception("[Migration] CRITICAL: Failed to ensure SQLite columns for live_signals/shadow_signals: %s", e)
        raise RuntimeError(f"Database migration failed: {e}") from e

def ensure_active_signal_idempotency_index():
    """
    Safely inspects existing active records for duplicate (symbol, timeframe) pairs,
    reports conflicts without deleting data, and creates the unique index if clean.
    """
    try:
        with engine.connect() as conn:
            tables = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='live_signals'")).fetchall()
            if not tables:
                return

            dups = conn.execute(text(
                "SELECT symbol, timeframe, COUNT(*) as cnt FROM live_signals WHERE status = 'ACTIVE' GROUP BY symbol, timeframe HAVING cnt > 1"
            )).fetchall()

            if dups:
                dup_list = [dict(row._mapping) for row in dups]
                logger.error("[Migration] CRITICAL: Existing duplicate active signals found for (symbol, timeframe): %s", dup_list)
                raise RuntimeError(f"Database migration blocked: Existing duplicate active signals found: {dup_list}. Manual reconciliation required.")

            conn.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS idx_unique_active_signal ON live_signals (symbol, timeframe) WHERE status = 'ACTIVE'"))
            conn.commit()
            logger.info("[Migration] Database partial unique index 'idx_unique_active_signal' verified successfully.")
    except Exception as e:
        if "Database migration blocked" in str(e):
            raise e
        logger.warning("[Migration] Active signal unique index verification notice: %s", e)

@app.on_event("startup")
def on_startup():
    """
    Non-destructive schema verification and safe database seeder on application startup.
    """
    logger.info("[Startup] Verifying non-destructive database tables...")
    Base.metadata.create_all(bind=engine)
    PostgresBase.metadata.create_all(bind=postgres_engine)
    ensure_sqlite_columns()
    ensure_active_signal_idempotency_index()

    try:
        from fastapi_cache import FastAPICache
        from fastapi_cache.backends.inmemory import InMemoryBackend
        FastAPICache.init(InMemoryBackend(), prefix="fastapi-cache")
        logger.info("[Startup] FastAPICache initialized successfully.")
    except Exception as e:
        logger.warning("[Startup] FastAPICache initialization warning: %s", e)

    seed_allowed = os.getenv("SEED_DATA_ALLOWED", "false").lower() == "true"
    if seed_allowed:
        logger.info("[Startup] Executing safe database seeder check (SEED_DATA_ALLOWED=true)...")
        seed_local_database()
    else:
        logger.info("[Startup] Seed data skipped (SEED_DATA_ALLOWED=false fail-closed guard).")
    logger.info("[Startup] TradeMindAI Local Offline Server ready.")

@app.get("/")
def root():
    return {
        "app": "TradeMindAI Local Server",
        "version": "v2.3.0-LOCAL",
        "mode": "100% OFFLINE",
        "docs": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
