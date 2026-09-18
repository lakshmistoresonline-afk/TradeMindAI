from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Dict, Any, Optional
from backend.core.container import container
from backend.core.auth import get_current_user
from backend.domain.models.ios import MarketRegime, MarketOpportunity, LiveSignal
import uuid
import datetime
import traceback

router = APIRouter()

@router.get("/regime", response_model=MarketRegime)
async def get_market_regime():
    try:
        regime = await container.ios_repo.get_latest_regime()
        if not regime:
            return MarketRegime(
                date=datetime.datetime.utcnow(), regime="SIDEWAYS", risk_mode="NEUTRAL",
                sentiment_score=0.5, volatility_index=15.0,
                description="Market analysis engine initialized. Calculating institutional bias..."
            )
        return regime
    except Exception as e:
        print(f"Error in get_market_regime: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/opportunities")
async def get_opportunities(limit: int = 20):
    try:
        active = await container.ios_repo.get_active_opportunities(limit=limit)
        if not active:
            return []

        results = []
        for o in active:
            is_dict = isinstance(o, dict)
            results.append({
                "id": str(o.get("id") if is_dict else getattr(o, "id", uuid.uuid4())),
                "symbol": str(o.get("symbol") if is_dict else getattr(o, "symbol", "UNK")),
                "type": str(o.get("type") if is_dict else getattr(o, "type", "MOMENTUM")),
                "conviction_score": float(o.get("conviction_score") if is_dict else getattr(o, "conviction_score", 0)),
                "ai_thesis": str(o.get("ai_thesis") if is_dict else getattr(o, "ai_thesis", "")),
                "indicators": list(o.get("indicators") if is_dict else getattr(o, "indicators", [])),
                "timestamp": datetime.datetime.utcnow().isoformat()
            })
        return results
    except Exception as e:
        print(f"Critical Error in get_opportunities: {e}")
        return []

@router.get("/signals/live")
async def get_live_signals_audit(limit: int = 100):
    import math
    from fastapi.encoders import jsonable_encoder

    def sanitize_obj(obj):
        if isinstance(obj, dict):
            return {k: sanitize_obj(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [sanitize_obj(i) for i in obj]
        elif isinstance(obj, float):
            if not math.isfinite(obj):
                return 0.0
        return obj

    try:
        signals = await container.ios_repo.get_active_live_signals()
        results = []
        for s in signals:
            clean_data = sanitize_obj(s.model_dump())
            results.append(clean_data)

        return jsonable_encoder(results[:limit])
    except Exception as e:
        print(f"[CRITICAL] Failed to fetch live signals: {e}")
        return []
