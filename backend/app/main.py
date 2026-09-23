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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TradeMindAI")

app = FastAPI(
    title="TradeMindAI Local Offline API",
    version="2.3.0-LOCAL",
    description="100% Offline Local Quantitative Signal & TA Engine"
)

# Enable CORS for local frontend execution
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Modular API Routers
app.include_router(health.router)
app.include_router(ticker.router)
app.include_router(indicators.router)
app.include_router(signals.router)
app.include_router(import_data.router)

@app.on_event("startup")
def on_startup():
    """
    Non-destructive schema verification and safe database seeder on application startup.
    """
    logger.info("[Startup] Verifying non-destructive database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("[Startup] Executing safe database seeder check...")
    seed_local_database()
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
