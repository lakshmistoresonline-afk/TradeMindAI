"""
================================================================================
TradeMindAI: Health API Endpoint
================================================================================
GET /api/v1/health: Local API and DB status monitor.
"""

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from backend.app.db.database import get_db

router = APIRouter(prefix="/api/v1", tags=["Health"])

@router.get("/health")
def get_health_status(db: Session = Depends(get_db)):
    """
    Returns local system, database, and offline ML status.
    """
    db_status = "ONLINE"
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"OFFLINE ({e})"

    return {
        "status": "ONLINE",
        "mode": "100% LOCAL OFFLINE",
        "database": db_status,
        "engine": "TradeMindAI Local Engine v2.3",
        "api_version": "v1"
    }
