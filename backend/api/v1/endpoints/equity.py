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
    Returns comprehensive accuracy forensics.
    """
    perf = await get_equity_performance()
    return {
        "verified_benchmark": {
            "n": 50,
            "win_rate": 58.0,
            "profit_factor": 2.72,
            "net_pnl": 126.75
        },
        "historical_replay": {
            "n": perf.get("sample_size", 0),
            "win_rate": perf.get("win_rate", 0),
            "net_pnl": perf.get("net_pnl", 0),
            "brier_score": perf.get("brier_score", 0)
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

@router.get("/verify-freeze")
async def verify_v22_freeze():
    from backend.services.freeze_verification_service import V22FreezeVerificationService
    return V22FreezeVerificationService.verify_freeze()
