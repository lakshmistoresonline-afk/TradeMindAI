"""
================================================================================
TradeMindAI: Health API Endpoint (Hardened REL-02 & TM-05)
================================================================================
Distinguishes liveness from readiness, avoids leaking database exceptions,
and returns service-unavailable status when configured database connections fail.
================================================================================
"""

import logging
from fastapi import APIRouter, Response, status
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from backend.app.db.database import engine as app_engine
from backend.core.postgres import engine as postgres_engine

logger = logging.getLogger("trademindai.health")
router = APIRouter(tags=["Health"])


def check_database(database_engine, label: str) -> bool:
    try:
        with database_engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True
    except SQLAlchemyError:
        logger.exception(
            "Health check failed for database component=%s",
            label,
        )
        return False


@router.get("/livez", include_in_schema=False)
def liveness():
    return {"status": "alive"}


@router.get("/readyz", include_in_schema=False)
def readiness(response: Response):
    app_db_ready = check_database(app_engine, "application")
    postgres_db_ready = check_database(postgres_engine, "postgres")

    if not app_db_ready or not postgres_db_ready:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {"status": "not_ready", "database_application": app_db_ready, "database_postgres": postgres_db_ready}

    return {"status": "ready", "database_application": True, "database_postgres": True}


@router.get("/api/v1/health", tags=["Health"])
def get_health_status(response: Response):
    """
    Legacy health status endpoint aligned with readiness probe.
    """
    app_db_ready = check_database(app_engine, "application")
    postgres_db_ready = check_database(postgres_engine, "postgres")

    if not app_db_ready or not postgres_db_ready:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {
            "status": "UNHEALTHY",
            "database_application": app_db_ready,
            "database_postgres": postgres_db_ready,
            "engine": "TradeMindAI Local Engine v2.3",
            "api_version": "v1"
        }

    return {
        "status": "ONLINE",
        "mode": "100% LOCAL OFFLINE",
        "database_application": "ONLINE",
        "database_postgres": "ONLINE",
        "engine": "TradeMindAI Local Engine v2.3",
        "api_version": "v1"
    }
