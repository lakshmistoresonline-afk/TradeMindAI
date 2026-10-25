"""
================================================================================
TradeMindAI: AI Signals API Endpoint
================================================================================
GET /api/v1/signals/{symbol}: Executes local SignalEngine and returns AI insights.
Fail-Closed Quarantine Enforcement: Returns 503 Service Unavailable while QUARANTINE_ACTIVE=True.
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.orm import Session
from backend.core.config import settings
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
    Fails closed when QUARANTINE_ACTIVE=True to prevent untrusted signal exposure.
    """
    if getattr(settings, "QUARANTINE_ACTIVE", True):
        raise HTTPException(
            status_code=503,
            detail="QUARANTINED: Signal API endpoints are currently quarantined pending authentic market data verification."
        )

    df = LocalMarketDataService.get_historical_data(symbol, limit=180)
    if df.empty:
        raise HTTPException(status_code=404, detail=f"No local market data found for symbol '{symbol}'")

    news = db.query(NewsArticle).filter(NewsArticle.symbol.ilike(symbol)).order_by(NewsArticle.published_at.desc()).first()
    news_text = news.content if news else ""

    res = SignalEngine.generate_signal(df, news_text)

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
