from fastapi import APIRouter, HTTPException, Depends, Security
from fastapi.security import APIKeyHeader
from typing import List, Dict, Any, Optional
import datetime
from datetime import timezone


from backend.core.postgres import SessionLocal, StockDB, ShadowSignalDB
from sqlalchemy import text
import json

from backend.core.config import settings
import secrets

router = APIRouter()
API_KEY_NAME = "X-Collector-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

def verify_collector_key(api_key: str = Security(api_key_header)):
    """
    P0 Hardening: Constant-time comparison for ingestion key.
    """
    if not api_key:
        raise HTTPException(status_code=401, detail="Authentication required")

    # Constant-time compare to prevent timing attacks
    if not secrets.compare_digest(api_key, settings.MARKET_DATA_INGEST_KEY):
        print(f"[SECURITY] Unauthorized ingestion attempt from {api_key[:4]}...")
        raise HTTPException(status_code=403, detail="Forbidden: Invalid ingestion credentials")
    return api_key


@router.post("/ingest")
async def ingest_market_data(payload: List[Dict[str, Any]], collector_key: str = Depends(verify_collector_key)):
    """
    Workstream 1: Ingests market data from local Open Data Gateway.
    Authoritative ingestion point for public NSE data.
    """
    processed = 0
    errors = 0

    with SessionLocal() as session:
        for item in payload:
            symbol = item.get("symbol")
            price = item.get("price")
            ts_str = item.get("timestamp")

            if not symbol or price is None:
                errors += 1
                continue

            try:
                # Update Stock Master (LTP)
                stock = session.query(StockDB).filter(StockDB.symbol == symbol).first()
                if stock:
                    stock.last_price = float(price)
                    stock.updated_at = datetime.fromisoformat(ts_str) if ts_str else datetime.now(timezone.utc)

                    processed += 1

                # Note: For signals, they resolve price via PriceResolver which now
                # looks at the updated last_price from database.
            except Exception as e:
                print(f"   [!] Ingestion Error for {symbol}: {e}")
                errors += 1

        session.commit()

    return {
        "status": "SUCCESS",
        "processed": processed,
        "errors": errors,
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get("/status")
async def get_market_data_status():
    """
    Returns the health of the open data fabric.
    """
    with SessionLocal() as session:
        total = session.query(StockDB).count()
        now = datetime.now(timezone.utc)
        fresh = session.query(StockDB).filter(StockDB.updated_at > now - datetime.timedelta(minutes=15)).count()

    return {
        "fabric_version": "v1.1.0", # Phase 3 Identity
        "source": "NSE_OPEN_DATA_GATEWAY",
        "total_universe": total,
        "fresh_count": fresh,
        "freshness_pct": (fresh / total * 100) if total > 0 else 0,
        "server_time": now.isoformat()
    }

