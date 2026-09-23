"""
================================================================================
TradeMindAI: AI Signals API Endpoint
================================================================================
GET /api/v1/signals/{symbol}: Executes local SignalEngine and returns AI insights.
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.orm import Session
from backend.app.db.database import get_db
from backend.app.db.models import NewsArticle, TradingSignal
from backend.app.services.market_data_service import LocalMarketDataService
from backend.app.services.signal_engine import SignalEngine
import json

router = APIRouter(prefix="/api/v1", tags=["Signals"])

@router.get("/signals/{symbol}")
def get_signal_for_symbol(symbol: str, db: Session = Depends(get_db)):
    """
    Executes local SignalEngine and returns AI insights derived offline.
    """
    df = LocalMarketDataService.get_historical_data(symbol, limit=180)
    if df.empty:
        raise HTTPException(status_code=404, detail=f"No local market data found for symbol '{symbol}'")

    # Fetch stored local news for sentiment analysis
    news = db.query(NewsArticle).filter(NewsArticle.symbol.ilike(symbol)).order_by(NewsArticle.published_at.desc()).first()
    news_text = news.content if news else ""

    # Execute Signal Engine
    res = SignalEngine.generate_signal(df, news_text)

    # Persist Signal to local TradingSignal table
    try:
        sig_record = TradingSignal(
            symbol=symbol.upper(),
            signal_type=res["signal_type"],
            confidence=res["confidence"],
            sentiment_score=res["sentiment_score"],
            drivers_json=json.dumps(res["drivers"])
        )
        db.add(sig_record)
        db.commit()
    except Exception:
        db.rollback()

    return {
        "symbol": symbol.upper(),
        "signal_type": res["signal_type"],
        "confidence": res["confidence"],
        "sentiment_score": res["sentiment_score"],
        "drivers": res["drivers"],
        "metrics": res["metrics"]
    }
