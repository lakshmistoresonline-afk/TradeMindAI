from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from typing import List
from backend.api.v1.api import api_router
from backend.core.config import settings
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis
import datetime
import json

app = FastAPI(
    title="TradeMind AI-IOS (Vision 2.0)",
    description="Institutional AI Investment Operating System API. Supports multi-agent consensus, predictive ML, and enterprise risk analytics.",
    version="2.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    contact={
        "name": "TradeMind AI Enterprise Support",
        "url": "https://trademindai.com",
    },
)

from backend.core.websocket import manager

@app.websocket("/ws/alerts")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text() # Keep connection alive
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.on_event("startup")
async def startup():
    redis = aioredis.from_url(settings.REDIS_URL, encoding="utf8", decode_responses=True)
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")

    # Auto-initialize SQL Schema on startup
    from backend.core.postgres import init_db
    try:
        print("Syncing Database Schema...")
        init_db()
        print("Database Schema Ready.")
    except Exception as e:
        print(f"Database Initialization Failed: {e}")

# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For development/testing, allow all. You can restrict to your web.app later.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    db_status = "READY"
    try:
        from backend.core.postgres import engine
        from sqlalchemy import text
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        db_type = "PostgreSQL (Neon)" if "neon" in str(engine.url) else "SQLite"
    except Exception as e:
        db_status = f"ERROR: {str(e)}"
        db_type = "UNKNOWN"

    return {
        "message": "Welcome to TradeMind AI API",
        "database": {
            "engine": db_type,
            "status": db_status
        },
        "version": "2.0.0-RC4.16"
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.datetime.utcnow()}

@app.get("/debug/db")
async def debug_db():
    from backend.core.container import container
    from backend.core.postgres import StockDB
    try:
        stocks = await container.repository.get_all_stocks(limit=5)
        return {"status": "SUCCESS", "count": len(stocks), "samples": [s.symbol for s in stocks]}
    except Exception as e:
        import traceback
        return {"status": "ERROR", "error": str(e), "trace": traceback.format_exc()}
