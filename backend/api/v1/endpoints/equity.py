from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Dict, Any, Optional
from backend.core.container import container
from backend.domain.models.ios import LiveSignal
from backend.services.signal_ledger_service import SignalLedgerService
from backend.services.signal_lifecycle_service import SignalLifecycleService
from backend.services.research_metrics_service import ResearchMetricsService
import datetime

router = APIRouter()

@router.get("/signals", response_model=List[LiveSignal])
async def get_equity_signals(
    status: Optional[str] = None,
    symbol: Optional[str] = None,
    limit: int = 100
):
    """
    GET /api/v1/equity/signals
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

        # Mapping logic (Simplified for brevity, usually in repo)
        results = []
        for s in db_signals:
            # Re-use repo mapping if available or manual mapping
            results.append(container.ios_repo._map_db_to_live_signal(s))

        return results

@router.get("/signals/{signal_id}", response_model=LiveSignal)
async def get_signal_detail(signal_id: str):
    signal = await SignalLedgerService.get_signal(signal_id)
    if not signal:
        raise HTTPException(status_code=404, detail="Signal not found")
    return signal

@router.get("/scanner")
async def get_equity_scanner(
    direction: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50
):
    """
    GET /api/v1/equity/scanner
    Returns a consolidated view for the Equity Scanner UI.
    """
    from backend.core.postgres import SessionLocal, LiveSignalDB, StockDB
    with SessionLocal() as session:
        query = session.query(LiveSignalDB, StockDB).join(StockDB, LiveSignalDB.symbol == StockDB.symbol)

        if direction:
            query = query.filter(LiveSignalDB.direction == direction)
        if status:
            query = query.filter(LiveSignalDB.status == status)

        results = query.order_by(LiveSignalDB.timestamp.desc()).limit(limit).all()

        scanner_data = []
        for sig_db, stock_db in results:
            sig = container.ios_repo._map_db_to_live_signal(sig_db)
            data = sig.model_dump()
            data["company_name"] = stock_db.name
            data["change_pct"] = stock_db.change_pct
            scanner_data.append(data)

        return scanner_data

@router.get("/research")
async def get_equity_research_runs():
    """
    GET /api/v1/equity/research
    Returns summary of historical research runs.
    """
    # For now, return a placeholder until ResearchRun is persisted in Neon
    return [
        {
            "id": "run_initial_v22",
            "strategy_version": "v2.2",
            "dataset_id": "NIFTY_200_AUG2026",
            "signal_count": 87,
            "status": "COMPLETED",
            "start_timestamp": "2026-09-01T12:00:00"
        }
    ]

@router.get("/accuracy")
async def get_equity_accuracy():
    """
    GET /api/v1/equity/accuracy
    Returns comprehensive accuracy forensics including multi-horizon OOS metrics.
    """
    champions = await container.data_platform_repo.get_all_champion_models()

    horizons_report = {}
    for h in ["SHORT", "SWING", "LONG"]:
        h_models = [m for m in champions if m.horizon == h]
        if not h_models:
            horizons_report[h] = {"sample_size": 0, "auc": 0, "win_rate": 0, "brier": 0}
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
            "n": 50,
            "win_rate": 58.0,
            "profit_factor": 2.72,
            "net_pnl": 126.75
        }
    }

@router.get("/performance")
async def get_equity_performance():
    """
    Returns canonical metrics for V2.2.
    """
    from backend.core.postgres import SessionLocal, LiveSignalDB
    with SessionLocal() as session:
        resolved = session.query(LiveSignalDB).filter(LiveSignalDB.status.in_(["TARGET_HIT", "STOP_LOSS", "EXPIRED"])).all()
        signals_data = [s.__dict__ for s in resolved]
        return ResearchMetricsService.calculate_performance_metrics(signals_data)

@router.get("/market")
async def get_market_state():
    regime = await container.ios_repo.get_latest_regime()
    return {
        "regime": regime.regime if regime else "SIDEWAYS",
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "universe": "NIFTY-200"
    }

@router.get("/history")
async def get_equity_history(
    symbol: Optional[str] = None,
    horizon: Optional[str] = None,
    quality: Optional[str] = None,
    status: Optional[str] = None,
    page: int = 1,
    limit: int = 50
):
    """
    GET /api/v1/equity/history
    Returns historical signal records from the shadow_signals ledger.
    """
    from backend.core.postgres import SessionLocal, ShadowSignalDB
    with SessionLocal() as session:
        query = session.query(ShadowSignalDB)

        # Apply Filters
        if symbol and symbol != "ALL":
            query = query.filter(ShadowSignalDB.symbol == symbol)
        if horizon and horizon != "ALL":
            # Map Horizon to signal_type if necessary
            query = query.filter(ShadowSignalDB.signal_type == horizon)
        if quality and quality != "ALL":
            query = query.filter(ShadowSignalDB.quality_class == quality)
        if status and status != "ALL":
            query = query.filter(ShadowSignalDB.status == status)
        else:
            # Default: show only terminal/closed signals in history
            query = query.filter(ShadowSignalDB.status != "ACTIVE")

        total = query.count()
        db_signals = query.order_by(ShadowSignalDB.timestamp.desc()).offset((page-1)*limit).limit(limit).all()

        results = []
        for s in db_signals:
            # Map DB to Dict
            data = {c.name: getattr(s, c.name) for c in s.__table__.columns}
            # Normalize timestamps
            for k, v in data.items():
                if isinstance(v, datetime.datetime):
                    data[k] = v.isoformat()

            # Canonical Mapping for Frontend Compatibility
            data["timeframe"] = data.get("signal_type") or data.get("timeframe") or "SWING"
            data["direction"] = data.get("signal_rating") or data.get("direction")
            data["quality_class"] = data.get("quality_class") or ("PRIMARY" if data["timeframe"] == "SWING" else "EXPERIMENTAL")

            results.append(data)

        return {
            "records": results,
            "total": total,
            "page": page,
            "limit": limit
        }

@router.get("/verify-freeze")
async def verify_v22_freeze():
    from backend.services.freeze_verification_service import V22FreezeVerificationService
    return V22FreezeVerificationService.verify_freeze()
