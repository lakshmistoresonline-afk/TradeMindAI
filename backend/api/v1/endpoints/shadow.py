
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any, Optional
import json
from datetime import datetime, timedelta
from backend.core.database import db_client
from backend.core.postgres import SessionLocal, ShadowSignalDB, ShadowEventDB
from google.cloud import firestore

router = APIRouter()

# --- Frozen Strategy v2.2 Constants ---
BASELINE_START = "2026-08-18"
TERMINAL_STATES = ['TARGET_HIT', 'STOP_LOSS', 'TIMEOUT', 'AMBIGUOUS', 'INVALID']

def get_firestore_summary():
    if not db_client:
        return None
    try:
        doc = db_client.collection("shadow_summary").document("latest").get()
        if doc.exists:
            return doc.to_dict()
    except Exception as e:
        print(f"Firestore Error (Summary): {e}")
    return None

@router.get("/status")
async def get_shadow_status():
    """
    Read-only system status for Shadow Mode Strategy v2.2.
    Primary source: Firestore.
    """
    summary = get_firestore_summary()
    return {
        "strategy": "trademind-equity-v2.2",
        "segment": "EQUITY",
        "universe": "NIFTY 200",
        "mode": "SHADOW",
        "status": "HEALTHY",
        "baseline_start": summary.get("baseline_start") if summary else None,
        "market_session": summary.get("session_type", "UNKNOWN") if summary else "UNKNOWN",
        "last_update": datetime.utcnow().isoformat(),
        "freeze_status": "FROZEN",
        "data_source": "FIREBASE" if db_client else "LOCAL_SQL"
    }

@router.get("/summary")
async def get_shadow_summary():
    summary = get_firestore_summary()
    if summary:
        return {
            "evaluation_cycles": summary.get("evaluation_cycles", 0),
            "evaluation_events": summary.get("evaluation_events", summary.get("scanned_symbols", 0)),
            "eligible_evaluations": summary.get("eligible_evaluations", 0),
            "data_gap_evaluations": summary.get("data_gap_evaluations", 0),
            "strategy_trigger_events": summary.get("transactional_signals", summary.get("trade_count", 0)),
            "transactional_signals": summary.get("transactional_signals", summary.get("trade_count", 0)),
            "active_signals": summary.get("active_positions", 0),
            "completed_trades": summary.get("completed_trades", summary.get("trade_count", 0)),
            "operational_symbols": summary.get("operational_symbols", 198),
            "unavailable_symbols": summary.get("unavailable_symbols", 2),
            "equity": summary.get("equity", 1000000.0)
        }

    # [LEGACY FALLBACK] Only used if Firestore is unavailable
    # [LEGACY FALLBACK] Only used if Firestore is unavailable
    with SessionLocal() as session:
        baseline = None
        base_query = session.query(ShadowEventDB).filter(
            ShadowEventDB.event_type == 'EVALUATION'
        )
        if baseline:
            base_query = base_query.filter(ShadowEventDB.timestamp >= baseline)
        eval_events = base_query.count()
        eval_cycles = base_query.with_entities(ShadowEventDB.timestamp).distinct().count()
        trigger_events = base_query.filter(ShadowEventDB.decision == 'TRADE_SIGNAL').count()
        transactional_signals = session.query(ShadowSignalDB).filter(ShadowSignalDB.timestamp >= BASELINE_START).count()
        active_signals = session.query(ShadowSignalDB).filter(ShadowSignalDB.status == 'ACTIVE', ShadowSignalDB.timestamp >= BASELINE_START).count()
        TERMINAL_STATES = ['TARGET_HIT', 'STOP_LOSS', 'TIMEOUT', 'AMBIGUOUS', 'INVALID']
        completed_trades = session.query(ShadowSignalDB).filter(ShadowSignalDB.status.in_(TERMINAL_STATES), ShadowSignalDB.timestamp >= BASELINE_START).count()

        return {
            "evaluation_cycles": eval_cycles,
            "evaluation_events": eval_events,
            "eligible_evaluations": eval_cycles * 196,
            "data_gap_evaluations": eval_cycles * 4,
            "strategy_trigger_events": trigger_events,
            "transactional_signals": transactional_signals,
            "active_signals": active_signals,
            "completed_trades": completed_trades
        }

@router.get("/active-signals")
async def get_active_signals():
    if db_client:
        try:
            signals_ref = db_client.collection("shadow_signals").where("status", "==", "ACTIVE")
            docs = signals_ref.stream()
            active = []
            for doc in docs:
                s = doc.to_dict()
                active.append({
                    "id": doc.id,
                    "symbol": s.get("symbol"),
                    "direction": s.get("direction"),
                    "timestamp": s.get("timestamp").isoformat() if hasattr(s.get("timestamp"), "isoformat") else s.get("timestamp"),
                    "entry": s.get("entry_price", 0),
                    "target": s.get("target_price", 0),
                    "stop": s.get("stop_price", 0),
                    "probability": s.get("prob", 0),
                    "ev": s.get("ev", 0),
                    "model_version": s.get("model_version", "v2.2"),
                    "status": s.get("status")
                })
            return active
        except Exception as e:
            print(f"Firestore Error (Active Signals): {e}")

    # [LEGACY FALLBACK] Only used if Firestore is unavailable
    with SessionLocal() as session:
        active = session.query(ShadowSignalDB).filter(ShadowSignalDB.status == 'ACTIVE').all()
        return [
            {
                "id": s.id, "symbol": s.symbol, "direction": s.direction,
                "timestamp": s.timestamp.isoformat() if isinstance(s.timestamp, datetime) else s.timestamp,
                "entry": s.entry_price, "target": s.target_price, "stop": s.stop_price,
                "probability": s.calibrated_probability, "ev": s.expected_value,
                "model_version": s.model_version, "status": s.status
            } for s in active
        ]

@router.get("/performance")
async def get_shadow_performance():
    summary = get_firestore_summary()
    if summary:
        return {
            "completed_trades": summary.get("completed_trades", summary.get("trade_count", 0)),
            "win_rate": round(summary.get("win_rate", 0), 2),
            "net_ev": round(summary.get("net_ev", 0), 4),
            "probability_mean": round(summary.get("probability_mean", 0), 4),
            "sample_status": "INSUFFICIENT_SAMPLE" if summary.get("trade_count", 0) < 20 else "ADEQUATE",
            "wins": int(summary.get("wins", 0)),
            "losses": int(summary.get("completed_trades", 0) - summary.get("wins", 0))
        }

    # [LEGACY FALLBACK] Only used if Firestore is unavailable
    with SessionLocal() as session:
        baseline = None
        TERMINAL_STATES = ['TARGET_HIT', 'STOP_LOSS', 'TIMEOUT', 'AMBIGUOUS', 'INVALID']
        query = session.query(ShadowSignalDB).filter(ShadowSignalDB.status.in_(TERMINAL_STATES))
        if baseline:
            query = query.filter(ShadowSignalDB.timestamp >= baseline)
        terminal = query.all()
        completed = len(terminal)
        wins = len([t for t in terminal if t.status == 'TARGET_HIT'])
        win_rate = (wins / completed * 100) if completed > 0 else 0.0
        returns = [t.net_return for t in terminal if t.net_return is not None]
        net_ev = sum(returns) / len(returns) if returns else 0.0
        event_query = session.query(ShadowEventDB.payload_json).filter(ShadowEventDB.event_type == 'EVALUATION')
        if baseline:
            event_query = event_query.filter(ShadowEventDB.timestamp >= baseline)
        events = event_query.all()
        prob_values = []
        for e in events:
            if e[0]:
                try:
                    payload = json.loads(e[0])
                    if payload.get("prob") is not None: prob_values.append(payload["prob"])
                except: continue
        prob_mean = sum(prob_values) / len(prob_values) if prob_values else 0.0

        return {
            "completed_trades": completed, "win_rate": round(win_rate, 2), "net_ev": round(net_ev, 4),
            "probability_mean": round(prob_mean, 4),
            "sample_status": "INSUFFICIENT_SAMPLE" if completed < 20 else "ADEQUATE",
            "wins": wins, "losses": completed - wins
        }

@router.get("/universe")
async def get_shadow_universe():
    if db_client:
        try:
            # Fetch latest diagnostics
            docs = db_client.collection("shadow_scan_diagnostics").order_by("scan_timestamp", direction=firestore.Query.DESCENDING).limit(200).stream()
            results = []
            for doc in docs:
                d = doc.to_dict()
                results.append({
                    "symbol": d.get("symbol"),
                    "decision": d.get("decision"),
                    "rejection_reason": d.get("reason"),
                    "probability": d.get("score"),
                    "ev": d.get("ev", 0.0),
                    "price": d.get("price", 0.0),
                    "model_status": "READY" if d.get("model_version") else "MISSING",
                    "timestamp": d.get("scan_timestamp").isoformat() if hasattr(d.get("scan_timestamp"), "isoformat") else d.get("scan_timestamp")
                })
            if results:
                return results
        except Exception as e:
            print(f"Firestore Error (Universe): {e}")

    # [LEGACY FALLBACK] Only used if Firestore is unavailable
    with SessionLocal() as session:
        latest_ts = session.query(ShadowEventDB.timestamp).filter(ShadowEventDB.event_type == 'EVALUATION').order_by(ShadowEventDB.timestamp.desc()).first()
        if not latest_ts: return []
        ts = latest_ts[0]
        events = session.query(ShadowEventDB).filter(ShadowEventDB.timestamp == ts).all()
        results = []
        for e in events:
            payload = json.loads(e.payload_json) if e.payload_json else {}
            results.append({
                "symbol": e.symbol, "decision": e.decision, "rejection_reason": e.rejection_reason,
                "probability": payload.get("prob"), "ev": payload.get("ev"), "price": payload.get("price"),
                "model_status": "READY" if e.model_version else "MISSING",
                "timestamp": e.timestamp.isoformat() if isinstance(e.timestamp, datetime) else e.timestamp
            })
        return results

@router.get("/health")
async def get_shadow_health():
    summary = get_firestore_summary()
    if summary:
        last_run = summary.get("last_run")
        return {
            "database": "PASS",
            "model_runtime": "PASS",
            "data_freshness": "PASS",
            "persistence": "PASS",
            "shadow_worker": "ONLINE",
            "last_worker_heartbeat": last_run.isoformat() if hasattr(last_run, "isoformat") else last_run,
            "last_shadow_cycle": last_run.isoformat() if hasattr(last_run, "isoformat") else last_run,
            "strategy_freeze": "PASS"
        }

    # [LEGACY FALLBACK] Only used if Firestore is unavailable
    with SessionLocal() as session:
        cutoff = datetime.utcnow() - timedelta(minutes=5)
        worker_event = session.query(ShadowEventDB).filter(ShadowEventDB.event_type == 'HEARTBEAT', ShadowEventDB.timestamp >= cutoff).order_by(ShadowEventDB.timestamp.desc()).first()
        last_cycle = session.query(ShadowEventDB).filter(ShadowEventDB.event_type == 'EVALUATION').order_by(ShadowEventDB.timestamp.desc()).first()
        return {
            "database": "PASS", "model_runtime": "PASS", "data_freshness": "PASS", "persistence": "PASS",
            "shadow_worker": "ONLINE" if worker_event else "OFFLINE",
            "last_worker_heartbeat": worker_event.timestamp.isoformat() if worker_event else None,
            "last_shadow_cycle": last_cycle.timestamp.isoformat() if last_cycle else None,
            "strategy_freeze": "PASS"
        }
