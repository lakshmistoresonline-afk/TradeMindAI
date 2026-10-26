"""
================================================================================
TradeMindAI Operational API: Health Checks and Graceful Shutdown (REL-02)
================================================================================
Provides a standalone ASGI application with /livez and /readyz, lifecycle management,
and a safe shutdown readiness transition.
================================================================================
"""

import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Response, status

logger = logging.getLogger("trademindai.operations")


class RuntimeState:
    def __init__(self):
        self.ready = False
        self.shutting_down = False


state = RuntimeState()


@asynccontextmanager
async def lifespan(app: FastAPI):
    state.shutting_down = False
    state.ready = True
    logger.info("Application started")

    try:
        yield
    finally:
        state.ready = False
        state.shutting_down = True
        logger.info("Application shutting down")
        await asyncio.sleep(0)


app = FastAPI(
    title="TradeMindAI Operational API",
    lifespan=lifespan,
    docs_url=None,
    redoc_url=None,
)


@app.get("/livez")
async def livez():
    return {"status": "alive"}


@app.get("/readyz")
async def readyz(response: Response):
    if state.shutting_down or not state.ready:
        response.status_code = (
            status.HTTP_503_SERVICE_UNAVAILABLE
        )
        return {"status": "not_ready"}

    return {"status": "ready"}
