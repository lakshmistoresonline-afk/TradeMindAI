"""
================================================================================
TradeMindAI: Ticker API Endpoint
================================================================================
GET /api/v1/ticker/{symbol}: Returns historical OHLCV data from local database.
"""

from fastapi import APIRouter, HTTPException, Query
from backend.app.services.market_data_service import LocalMarketDataService

router = APIRouter(prefix="/api/v1", tags=["Ticker"])

@router.get("/ticker/{symbol}")
def get_ticker_data(symbol: str, limit: int = Query(180, ge=10, le=1000)):
    """
    Retrieves historical OHLCV price time-series for a given symbol from local DB.
    """
    df = LocalMarketDataService.get_historical_data(symbol, limit)
    if df.empty:
        raise HTTPException(status_code=404, detail=f"No local market data found for symbol '{symbol}'")

    records = df.to_dict(orient="records")
    for r in records:
        if "timestamp" in r and hasattr(r["timestamp"], "isoformat"):
            r["timestamp"] = r["timestamp"].isoformat()

    return {
        "symbol": symbol.upper(),
        "count": len(records),
        "data": records
    }

@router.get("/symbols")
def get_symbols():
    """
    Returns list of all available symbols in the local database.
    """
    symbols = LocalMarketDataService.get_available_symbols()
    return {"symbols": symbols, "count": len(symbols)}
