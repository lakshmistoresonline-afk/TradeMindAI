"""
================================================================================
TradeMindAI: Local Offline FastAPI Application Entry Point
================================================================================
100% Offline Local Operation Application Server.
Incorporates modular routers and non-destructive database auto-seeding on startup.
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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

# Enable CORS for local and production deployment
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8000",
        "https://com-webcraft-trademindai-c8f75.web.app",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Canonical V1 API Router and Modular Local Routers
app.include_router(api_router, prefix="/api/v1")
app.include_router(health.router)
app.include_router(ticker.router)
app.include_router(indicators.router)
app.include_router(signals.router)
app.include_router(import_data.router)

from backend.core.postgres import Base as PostgresBase, engine as postgres_engine

@app.on_event("startup")
def on_startup():
    """
    Non-destructive schema verification and safe database seeder on application startup.
    """
    logger.info("[Startup] Verifying non-destructive database tables...")
    Base.metadata.create_all(bind=engine)
    PostgresBase.metadata.create_all(bind=postgres_engine)

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
