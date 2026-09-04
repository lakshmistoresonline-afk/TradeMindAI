from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.core.postgres import get_pg_db, SessionLocal, StockDB, ShadowSignalDB
import datetime

router = APIRouter()

@router.get("/")
def get_system_health(db: Session = Depends(get_pg_db)):
    """
    Workstream 35: Production Observability health checks.
    """
    now = datetime.datetime.utcnow()

    # 1. Database Check
    try:
        db.execute(text("SELECT 1"))
        db_status = "HEALTHY"
    except:
        db_status = "ERROR"

    # 2. Market Data Freshness
    stale_stocks = db.query(StockDB).filter(StockDB.updated_at < now - datetime.timedelta(hours=24)).count()
    data_status = "HEALTHY" if stale_stocks < 10 else "DEGRADED"

    # 3. Active Signals
    active_count = db.query(ShadowSignalDB).filter(ShadowSignalDB.status == 'ACTIVE').count()

    return {
        "status": "ONLINE",
        "timestamp": now.isoformat(),
        "database": db_status,
        "market_data": {
            "status": data_status,
            "stale_stock_count": stale_stocks
        },
        "active_signals": active_count,
        "milestone": "50/50_COMPLETE"
    }

from sqlalchemy import text
