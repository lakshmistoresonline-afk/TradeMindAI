"""
================================================================================
TradeMindAI: Health API Endpoint (Hardened REL-02 & TM-05)
================================================================================
GET /api/v1/health: System and DB status monitor with fail-closed 503 on dependency failure.
================================================================================
"""

import logging
from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import text
from sqlalchemy.orm import Session
from backend.app.db.database import get_db

logger = logging.getLogger("trademindai.health")
router = APIRouter(prefix="/api/v1", tags=["Health"])

@router.get("/health")
def get_health_status(response: Response, db: Session = Depends(get_db)):
    """
    Returns system and database health. Returns 503 if critical dependencies fail.
    """
    db_status = "ONLINE"
    healthy = True
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        logger.error(f"[Health Check] Database connectivity check failed: {e}")
        db_status = "OFFLINE"
        healthy = False

    if not healthy:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {
            "status": "UNHEALTHY",
            "database": db_status,
            "engine": "TradeMindAI Local Engine v2.3",
            "api_version": "v1"
        }

    return {
        "status": "ONLINE",
        "mode": "100% LOCAL OFFLINE",
        "database": db_status,
        "engine": "TradeMindAI Local Engine v2.3",
        "api_version": "v1"
    }
