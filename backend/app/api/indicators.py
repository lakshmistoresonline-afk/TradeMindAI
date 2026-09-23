"""
================================================================================
TradeMindAI: Technical Indicators API Endpoint
================================================================================
GET /api/v1/indicators/{symbol}: Calculates and returns TA metrics on demand from local DB records.
"""

from fastapi import APIRouter, HTTPException, Query
from backend.app.services.market_data_service import LocalMarketDataService
from backend.app.services.indicator_service import LocalIndicatorService

router = APIRouter(prefix="/api/v1", tags=["Indicators"])

@router.get("/indicators/{symbol}")
def get_indicators(symbol: str, limit: int = Query(180, ge=20, le=1000)):
    """
    Calculates RSI, MACD, EMAs, and Bollinger Bands on demand from local DB price records.
    """
    df = LocalMarketDataService.get_historical_data(symbol, limit)
    if df.empty:
        raise HTTPException(status_code=404, detail=f"No local market data found for symbol '{symbol}'")

    metrics = LocalIndicatorService.get_latest_metrics(df)
    metrics["symbol"] = symbol.upper()

    return {
        "symbol": symbol.upper(),
        "metrics": metrics
    }
