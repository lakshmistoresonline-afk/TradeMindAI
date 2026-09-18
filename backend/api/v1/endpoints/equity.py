from fastapi import APIRouter, HTTPException, Query, Depends
from backend.core.auth import get_current_user
from typing import List, Dict, Any, Optional
from sqlalchemy import func, or_
from backend.core.container import container
from backend.domain.models.ios import LiveSignal
from backend.services.signal_ledger_service import SignalLedgerService
from backend.services.signal_lifecycle_service import SignalLifecycleService
from backend.services.research_metrics_service import ResearchMetricsService
from backend.services.forensic_analytical_service import ForensicAnalyticalService
import datetime
import json

router = APIRouter()

@router.get("/signals", response_model=List[LiveSignal])
async def get_equity_signals(
    status: Optional[str] = None,
    symbol: Optional[str] = None,
    limit: int = 100
):
    """
    Returns complete signal records from the authoritative Neon ledger.
    """
    from backend.core.postgres import SessionLocal, LiveSignalDB
    with SessionLocal() as session:
        query = session.query(LiveSignalDB)
        if status:
            query = query.filter(LiveSignalDB.status == status)
        if symbol:
            query = query.filter(LiveSignalDB.symbol == symbol)

        db_signals = query.order_by(LiveSignalDB.timestamp.desc()).limit(limit).all()
        return [container.ios_repo._map_db_to_live_signal(s) for s in db_signals]

@router.get("/signals/{signal_id}", response_model=LiveSignal)
async def get_signal_detail(signal_id: str):
    signal = await SignalLedgerService.get_signal(signal_id)
    if not signal:
        raise HTTPException(status_code=404, detail="Signal not found")
    return signal

@router.get("/signals/{signal_id}/explanation")
def get_signal_explanation(signal_id: str):
    """
    Explainability (Why this signal?).
    """
    from backend.core.postgres import SessionLocal, IntelligenceSynthesisDB
    with SessionLocal() as session:
        res = session.query(IntelligenceSynthesisDB).filter(IntelligenceSynthesisDB.id == signal_id).first()
        if res:
            data = {c.name: getattr(res, c.name) for c in res.__table__.columns}
            json_cols = ["market_context", "sector_context", "technical_context", "supporting_evidence", "risk_factors"]
            for col in json_cols:
                if data.get(col): data[col] = json.loads(data[col])
            return data
    return {"status": "NOT_FOUND"}

@router.get("/accuracy")
async def get_equity_accuracy():
    """
    GET /api/v1/equity/accuracy
    Returns authoritative accuracy forensics derived from the 50-signal ledger (N=49 binary population).
    """
    from backend.core.postgres import SessionLocal, ShadowSignalDB
    with SessionLocal() as session:
        resolved = session.query(ShadowSignalDB).filter(ShadowSignalDB.status.in_(["TARGET_HIT", "STOP_LOSS", "EXPIRED"])).all()
        signals_data = []
        for s in resolved:
            data = {c.name: getattr(s, c.name) for c in s.__table__.columns}
            signals_data.append(data)

        perf = ResearchMetricsService.calculate_performance_metrics(signals_data)

        # Multi-horizon champions
        champions = await container.data_platform_repo.get_all_champion_models()
        horizons_report = {}
        for h in ["SHORT", "SWING", "LONG"]:
            h_models = [m for m in champions if m.horizon == h]
            if not h_models:
                horizons_report[h] = {"sample_size": 0, "auc": 0, "win_rate": 0, "brier": 0, "logloss": 0, "ece": 0}
                continue

            horizons_report[h] = {
                "sample_size": len(h_models),
                "auc": sum(m.roc_auc for m in h_models) / len(h_models),
                "win_rate": sum(m.accuracy for m in h_models) * 100 / len(h_models),
                "brier": sum(m.brier_score for m in h_models) / len(h_models),
                "logloss": sum((m.calibration_metadata or {}).get("log_loss_calibrated", 0.69) for m in h_models) / len(h_models),
                "ece": sum((m.calibration_metadata or {}).get("ece", 0.0) for m in h_models) / len(h_models)
            }

    return {
        "horizons": horizons_report,
        "verified_benchmark": {
            "n": perf["sample_size"],
            "win_rate": perf["win_rate"],
            "profit_factor": perf["profit_factor"],
            "net_pnl": perf["net_pnl"]
        }
    }

@router.get("/performance")
async def get_equity_performance():
    """
    Returns canonical metrics for V2.2 directly from the Shadow Signal Ledger.
    """
    from backend.core.postgres import SessionLocal, ShadowSignalDB
    with SessionLocal() as session:
        resolved = session.query(ShadowSignalDB).filter(ShadowSignalDB.status.in_(["TARGET_HIT", "STOP_LOSS", "EXPIRED"])).all()
        signals_data = []
        for s in resolved:
            data = {c.name: getattr(s, c.name) for c in s.__table__.columns}
            signals_data.append(data)
        return ResearchMetricsService.calculate_performance_metrics(signals_data)

@router.get("/market")
async def get_market_state():
    from backend.services.market_data_service import MarketDataService
    return await MarketDataService.get_market_state()

@router.get("/status")
def get_strategy_status():
    from backend.services.market_calendar import MarketCalendar
    from backend.core.config import settings

    return {
        "strategy": "trademind-equity-v2.2",
        "universe": "NIFTY 200",
        "mode": "SHADOW_SIGNAL",
        "status": "ONLINE",
        "freeze_status": "FROZEN",
        "environment": settings.ENVIRONMENT,
        "market_open": MarketCalendar.is_market_open(),
        "timestamp": datetime.datetime.utcnow().isoformat()
    }

@router.get("/history")
async def get_equity_history(
    symbol: Optional[str] = None,
    horizon: Optional[str] = None,
    quality: Optional[str] = None,
    status: Optional[str] = None,
    direction: Optional[str] = None,
    page: int = 1,
    limit: int = 50,
    user: dict = Depends(get_current_user)
):
    """
    Returns historical signal records from the shadow_signals ledger.
    """
    from backend.core.postgres import SessionLocal, ShadowSignalDB
    with SessionLocal() as session:
        query = session.query(ShadowSignalDB)

        if symbol and symbol != "ALL":
            query = query.filter(or_(ShadowSignalDB.symbol.ilike(f"%{symbol}%"), ShadowSignalDB.id.ilike(f"%{symbol}%")))
        if horizon and horizon != "ALL":
            query = query.filter(ShadowSignalDB.signal_type == horizon)
        if quality and quality != "ALL":
            query = query.filter(ShadowSignalDB.quality_class == quality)
        if direction and direction != "ALL":
            if direction == "LONG":
                query = query.filter(or_(ShadowSignalDB.direction == "LONG", ShadowSignalDB.signal_rating == "BUY"))
            else:
                query = query.filter(or_(ShadowSignalDB.direction == "SHORT", ShadowSignalDB.signal_rating == "SELL"))
        if status and status != "ALL":
            query = query.filter(ShadowSignalDB.status == status)
        else:
            query = query.filter(ShadowSignalDB.status != "ACTIVE")

        total = query.count()
        base_query = session.query(ShadowSignalDB).filter(ShadowSignalDB.status != "ACTIVE")

        # Summary for filtered set
        target_hits = base_query.filter(ShadowSignalDB.status == "TARGET_HIT").count()
        stop_losses = base_query.filter(ShadowSignalDB.status == "STOP_LOSS").count()
        expired = base_query.filter(ShadowSignalDB.status == "EXPIRED").count()

        db_signals = query.order_by(ShadowSignalDB.timestamp.desc()).offset((page-1)*limit).limit(limit).all()

        results = []
        for s in db_signals:
            data = {c.name: getattr(s, c.name) for c in s.__table__.columns}
            for k, v in data.items():
                if isinstance(v, datetime.datetime): data[k] = v.isoformat()
            data["timeframe"] = data.get("signal_type") or data.get("timeframe") or "SWING"
            data["direction"] = data.get("signal_rating") or data.get("direction")
            results.append(data)

        return {
            "records": results,
            "total": total,
            "summary": {
                "total": base_query.count(),
                "target_hits": target_hits,
                "stop_losses": stop_losses,
                "expired": expired
            }
        }

@router.get("/verify-freeze")
async def verify_v22_freeze():
    from backend.services.freeze_verification_service import V22FreezeVerificationService
    return V22FreezeVerificationService.verify_freeze()
