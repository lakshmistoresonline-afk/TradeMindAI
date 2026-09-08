from fastapi import APIRouter, HTTPException, Depends, Security
from fastapi.security import APIKeyHeader
from typing import List, Dict, Any, Optional
from datetime import datetime
from backend.core.postgres import SessionLocal, StockDB, ShadowSignalDB
from sqlalchemy import text
import json

router = APIRouter()
API_KEY_NAME = "X-Collector-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

def verify_collector_key(api_key: str = Security(api_key_header)):
    # Simple hardcoded key for local gateway in Phase 1
    # In production, this should be a managed secret.
    if api_key != "trademind-open-gateway-v1":
        raise HTTPException(status_code=403, detail="Invalid Collector Key")
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
                    stock.updated_at = datetime.fromisoformat(ts_str) if ts_str else datetime.utcnow()
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
        fresh = session.query(StockDB).filter(StockDB.updated_at > datetime.utcnow() - datetime.timedelta(minutes=15)).count()

    return {
        "fabric_version": "v1.0.0",
        "source": "NSE_OPEN_DATA_GATEWAY",
        "total_universe": total,
        "fresh_count": fresh,
        "freshness_pct": (fresh / total * 100) if total > 0 else 0
    }
