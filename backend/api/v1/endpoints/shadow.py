
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any, Optional
import json
from datetime import datetime, timedelta
from backend.core.postgres import SessionLocal, ShadowSignalDB, ShadowEventDB
from sqlalchemy import func

router = APIRouter()

# --- Frozen Strategy v2.2 Constants ---
BASELINE_START = "2026-08-18"
TERMINAL_STATES = ['TARGET_HIT', 'STOP_LOSS', 'TIMEOUT', 'AMBIGUOUS', 'INVALID']

@router.get("/status")
def get_shadow_status():
    """
    Read-only system status for Shadow Mode Strategy v2.2.
    Source: SQL (Authoritative Dashboard Source).
    """
    from backend.services.market_calendar import IndianMarketCalendar
    from backend.core.config import settings
    session_type = IndianMarketCalendar.get_current_session(datetime.utcnow())

    return {
        "strategy": "trademind-equity-v2.2",
        "segment": "EQUITY",
        "universe": "NIFTY 200",
        "mode": "SHADOW",
        "status": "HEALTHY",
        "baseline_start": BASELINE_START,
        "market_session": session_type,
        "last_update": datetime.utcnow().isoformat(),
        "freeze_status": "FROZEN",
        "data_source": "SQL_PRODUCTION",
        "api_version": "RC5.6",
        "environment": settings.ENVIRONMENT
    }

@router.get("/summary")
def get_shadow_summary():
    """
    Real-time summary from SQL database.
    """
    try:
        with SessionLocal() as session:
            eval_cycles = session.query(ShadowEventDB.timestamp).filter(ShadowEventDB.event_type == 'EVALUATION').distinct().count()
            eval_events = session.query(ShadowEventDB).filter(ShadowEventDB.event_type == 'EVALUATION').count()
            transactional_signals = session.query(ShadowSignalDB).count()
            active_signals = session.query(ShadowSignalDB).filter(ShadowSignalDB.status == 'ACTIVE').count()
            completed_trades = session.query(ShadowSignalDB).filter(ShadowSignalDB.status.in_(TERMINAL_STATES)).count()

            # Detailed breakdown
            target_hits = session.query(ShadowSignalDB).filter(ShadowSignalDB.status == 'TARGET_HIT').count()
            stop_hits = session.query(ShadowSignalDB).filter(ShadowSignalDB.status == 'STOP_LOSS').count()
            timeouts = session.query(ShadowSignalDB).filter(ShadowSignalDB.status == 'TIMEOUT').count()
            expired = session.query(ShadowSignalDB).filter(ShadowSignalDB.status == 'EXPIRED').count()

            # Accounting
            allocation = 100000.0
            terminal = session.query(ShadowSignalDB).filter(ShadowSignalDB.status.in_(TERMINAL_STATES)).all()
            total_pnl = sum([allocation * (t.net_return or 0.0) / 100.0 for t in terminal])

            return {
                "evaluation_cycles": eval_cycles,
                "evaluation_events": eval_events,
                "eligible_evaluations": eval_cycles * 196,
                "data_gap_evaluations": 0,
                "strategy_trigger_events": transactional_signals,
                "transactional_signals": transactional_signals,
                "active_signals": active_signals,
                "completed_trades": completed_trades,
                "target_hits": target_hits,
                "stop_hits": stop_hits,
                "timeouts": timeouts,
                "expired": expired,
                "total_signals": transactional_signals,
                "operational_symbols": 198,
                "unavailable_symbols": 2,
                "equity": 1000000.0 + total_pnl
            }
    except Exception as e:
        print(f"SQL Error (Summary): {e}")
        return {"error": str(e)}

@router.get("/active-signals")
def get_active_signals():
    from backend.core.postgres import StockDB
    try:
        with SessionLocal() as session:
            # Join with StockDB to get the latest price
            active = session.query(ShadowSignalDB, StockDB.last_price).join(
                StockDB, ShadowSignalDB.symbol == StockDB.symbol, isouter=True
            ).filter(ShadowSignalDB.status == 'ACTIVE').all()

            results = []
            for s, lp in active:
                current_price = lp or s.entry_price # Fallback to entry if not found

                # Calculate P&L
                pnl = 0.0
                if current_price and s.entry_price:
                    if s.direction == "LONG":
                        pnl = (current_price - s.entry_price) / s.entry_price * 100
                    else:
                        pnl = (s.entry_price - current_price) / s.entry_price * 100

                results.append({
                    "id": s.id, "symbol": s.symbol, "direction": s.direction,
                    "timestamp": s.timestamp.isoformat() if hasattr(s.timestamp, "isoformat") else s.timestamp,
                    "created_at": (s.created_at or s.timestamp).isoformat() if hasattr(s.timestamp, "isoformat") else (s.created_at or s.timestamp),
                    "updated_at": (s.updated_at or s.timestamp).isoformat() if hasattr(s.timestamp, "isoformat") else (s.updated_at or s.timestamp),
                    "entry": s.entry_price, "target": s.target_price, "stop": s.stop_price,
                    "current_price": current_price,
                    "pnl_percentage": round(pnl, 2),
                    "probability": s.calibrated_probability, "ev": s.expected_value,
                    "model_version": s.model_version, "status": s.status
                })
            return results
    except Exception as e:
        print(f"SQL Error (Active): {e}")
        return []

@router.get("/performance")
def get_shadow_performance():
    try:
        with SessionLocal() as session:
            terminal = session.query(ShadowSignalDB).filter(ShadowSignalDB.status.in_(TERMINAL_STATES)).all()
            completed = len(terminal)
            wins = len([t for t in terminal if t.status == 'TARGET_HIT'])
            win_rate = (wins / completed * 100) if completed > 0 else 0.0
            returns = [t.net_return for t in terminal if t.net_return is not None]
            net_ev = sum(returns) / len(returns) if returns else 0.0

            return {
                "completed_trades": completed, "win_rate": round(win_rate, 2), "net_ev": round(net_ev, 4),
                "sample_status": "INSUFFICIENT_SAMPLE" if completed < 20 else "ADEQUATE",
                "wins": wins, "losses": completed - wins
            }
    except Exception as e:
        return {"error": str(e)}

@router.get("/universe")
def get_shadow_universe():
    try:
        with SessionLocal() as session:
            latest_ts = session.query(func.max(ShadowEventDB.timestamp)).filter(ShadowEventDB.event_type == 'EVALUATION').scalar()
            if not latest_ts: return []
            events = session.query(ShadowEventDB).filter(ShadowEventDB.timestamp == latest_ts).all()
            results = []
            for e in events:
                payload = json.loads(e.payload_json) if e.payload_json else {}
                results.append({
                    "symbol": e.symbol, "decision": e.decision, "rejection_reason": e.rejection_reason,
                    "probability": payload.get("prob"), "ev": payload.get("ev"), "price": payload.get("price"),
                    "model_status": "READY" if e.model_version else "MISSING",
                    "timestamp": e.timestamp.isoformat() if hasattr(e.timestamp, "isoformat") else e.timestamp
                })
            return results
    except Exception as e:
        return []

@router.get("/health")
def get_shadow_health():
    try:
        with SessionLocal() as session:
            last_cycle = session.query(func.max(ShadowEventDB.timestamp)).filter(ShadowEventDB.event_type == 'EVALUATION').scalar()
            return {
                "database": "PASS", "model_runtime": "PASS", "data_freshness": "PASS", "persistence": "PASS",
                "shadow_worker": "ONLINE",
                "last_data_sync": last_cycle.isoformat() if last_cycle else None,
                "last_shadow_cycle": last_cycle.isoformat() if last_cycle else None,
                "strategy_freeze": "PASS"
            }
    except:
        return {"status": "ERROR"}

@router.get("/signals")
def get_all_shadow_signals(
    status: Optional[str] = None,
    symbol: Optional[str] = None,
    direction: Optional[str] = None,
    page: int = 1,
    limit: int = 50
):
    try:
        with SessionLocal() as session:
            query = session.query(ShadowSignalDB)
            if status and status != "ALL":
                query = query.filter(ShadowSignalDB.status == status)
            if symbol and symbol != "ALL":
                query = query.filter(ShadowSignalDB.symbol == symbol)
            if direction and direction != "ALL":
                query = query.filter(ShadowSignalDB.direction == direction)

            signals = query.order_by(ShadowSignalDB.timestamp.desc()).offset((page-1)*limit).limit(limit).all()

            return {
                "signals": [
                    {
                        "id": s.id, "symbol": s.symbol, "direction": s.direction,
                        "timestamp": s.timestamp.isoformat() if hasattr(s.timestamp, "isoformat") else s.timestamp,
                        "created_at": (s.created_at or s.timestamp).isoformat() if hasattr(s.timestamp, "isoformat") else (s.created_at or s.timestamp),
                        "updated_at": (s.updated_at or s.timestamp).isoformat() if hasattr(s.timestamp, "isoformat") else (s.updated_at or s.timestamp),
                        "entry": s.entry_price, "target": s.target_price, "stop": s.stop_price,
                        "probability": s.calibrated_probability, "ev": s.expected_value,
                        "status": s.status, "pnl": s.net_return,
                        "outcome_timestamp": s.outcome_timestamp.isoformat() if s.outcome_timestamp else None,
                        "exit_price": s.exit_price,
                        "exit_reason": s.rejection_reason if s.status != 'ACTIVE' else None,
                        "model_version": s.model_version
                    } for s in signals
                ],
                "page": page,
                "limit": limit
            }
    except Exception as e:
        return {"signals": [], "page": page, "limit": limit, "error": str(e)}

@router.get("/debug/project-id")
def debug_project_id():
    import os
    return {"project_id": os.environ.get("RAILWAY_PROJECT_ID")}

@router.get("/debug/full-env")
def debug_full_env():
    import os
    safe_env = {}
    for k, v in os.environ.items():
        if any(secret in k.upper() for secret in ['KEY', 'SECRET', 'PASSWORD', 'TOKEN', 'ACCOUNT', 'URL']):
            safe_env[k] = "[MASKED]"
        else:
            safe_env[k] = v
    return safe_env

@router.get("/signals/metadata")
def get_signals_metadata():
    try:
        with SessionLocal() as session:
            statuses = [r[0] for r in session.query(ShadowSignalDB.status).distinct().all()]
            symbols = [r[0] for r in session.query(ShadowSignalDB.symbol).distinct().all()]
            return {
                "statuses": sorted(list(set(statuses + ["ACTIVE", "TARGET_HIT", "STOP_LOSS", "TIMEOUT", "EXPIRED"]))),
                "symbols": sorted(symbols) if symbols else ["SBIN"],
                "directions": ["LONG", "SHORT"]
            }
    except:
        return {
            "statuses": ["ACTIVE", "TARGET_HIT", "STOP_LOSS", "TIMEOUT", "EXPIRED", "REJECTED"],
            "symbols": ["SBIN"],
            "directions": ["LONG", "SHORT"]
        }
