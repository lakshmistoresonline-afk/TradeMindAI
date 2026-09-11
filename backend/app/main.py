from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import JSONResponse
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
import traceback
import asyncio

app = FastAPI(
    title="TradeMind AI MASTER 4.5.40A",
    description="Institutional AI Investment Operating System API.",
    version="2.0.0-RC5.8",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

@app.on_event("startup")
async def startup():
    print("[*] API Node ready.")
    # Async background task for non-critical inits
    async def background_inits():
        try:
            # 1. Redis
            redis = aioredis.from_url(
                settings.REDIS_URL,
                encoding="utf8",
                decode_responses=True,
                socket_timeout=1,
                socket_connect_timeout=1
            )
            FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
            print("[+] Redis Cache Standby.")
        except: pass

    asyncio.create_task(background_inits())

@app.get("/")
def root():
    return {
        "message": "Welcome to TradeMind AI API",
        "status": "ONLINE",
        "version": "2.0.0-PROD-RC5.8-FINAL-CERT",
        "deployed_at": datetime.datetime.utcnow().isoformat(),
        "forensic_id": "CERT_SYNC_20260911_1910"
    }

@app.get("/ready")
async def readiness():
    """
    Ready: required dependencies available.
    """
    status = {"status": "ready", "dependencies": {}}

    # 1. Database
    try:
        from backend.core.postgres import SessionLocal
        with SessionLocal() as session:
            session.execute(text("SELECT 1"))
        status["dependencies"]["postgres"] = "UP"
    except:
        status["dependencies"]["postgres"] = "DOWN"
        status["status"] = "not_ready"

    # 2. Redis
    try:
        from redis import asyncio as aioredis
        redis = aioredis.from_url(settings.REDIS_URL)
        await redis.ping()
        status["dependencies"]["redis"] = "UP"
        await redis.close()
    except:
        status["dependencies"]["redis"] = "DOWN"
        status["status"] = "not_ready"

    return status

@app.get("/health")
def health():
    return {"status": "healthy", "timestamp": datetime.datetime.utcnow().isoformat()}

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://com-webcraft-trademindai-c8f75.web.app",
        "https://com-webcraft-trademindai-c8f75.firebaseapp.com",
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    print(f"CRITICAL ERROR: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)},
    )
