from fastapi import APIRouter, Depends
from backend.core.auth import get_current_user, get_current_admin
from backend.core.container import container
import datetime
from datetime import timezone
from backend.services.universe_service import UniverseService


router = APIRouter()

@router.get("/stats")
async def get_system_stats(current_user: dict = Depends(get_current_admin)):
    """
    Returns high-level system summary (Real-time).
    """
    from backend.core.postgres import SessionLocal, LiveSignalDB, ShadowSignalDB
    with SessionLocal() as session:
        active = session.query(LiveSignalDB).count()
        total_hist = session.query(ShadowSignalDB).count()

    return {
        "active_signals": active,
        "historical_signals": total_hist,
        "system_health": "OPTIMAL"
    }

@router.get("/evaluation")
async def get_model_evaluation(current_user: dict = Depends(get_current_admin)):
    # Returns champion performance across universe
    return await container.data_platform_repo.get_all_champion_models()

@router.get("/db-audit")
async def db_audit(current_user: dict = Depends(get_current_admin)):
    from backend.core.postgres import engine
    from sqlalchemy import text
    results = {}
    with engine.connect() as conn:
        tables = ["stocks", "opportunities", "predictions", "historical_prices", "live_signals", "shadow_signals", "signal_shadow_decisions"]
        for t in tables:
            try:
                count = conn.execute(text(f"SELECT count(*) FROM {t}")).scalar()
                results[t] = count
            except:
                results[t] = "ERROR"
    return results

@router.get("/shadow-analytics")
async def get_shadow_analytics(current_user: dict = Depends(get_current_admin)):
    """
    V2.3 Shadow Analytics (Institutional 4.0).
    Aggregates comparisons between V2.2 and V2.3.
    """
    from backend.core.postgres import SessionLocal, SignalShadowDecisionDB
    from backend.services.signal_replay_engine import SignalReplayEngine

    with SessionLocal() as db:
        total = db.query(SignalShadowDecisionDB).count()
        blocked = db.query(SignalShadowDecisionDB).filter(SignalShadowDecisionDB.shadow_decision == "BLOCK").count()

        # Performance Attribution (Forward only - limited sample)
        # In a real system, we'd join with original outcome.

    replay = await SignalReplayEngine.replay_shadow_gate(limit=100)

    return {
        "forward": {
            "total_candidates": total,
            "v23_blocked": blocked,
            "v23_yield_pct": ((total - blocked) / total * 100) if total > 0 else 0
        },
        "replay": replay
    }

@router.get("/logs")
async def get_system_logs(limit: int = 20, current_user: dict = Depends(get_current_admin)):
    """
    Retrieves real-time forensic logs from the AI background workers.
    """
    from backend.core.database import db_client
    from google.cloud import firestore
    docs = db_client.collection("system_logs")\
        .order_by("timestamp", direction=firestore.Query.DESCENDING)\
        .limit(limit).stream()
    return [doc.to_dict() for doc in docs]
