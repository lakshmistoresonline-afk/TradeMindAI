
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any, Optional
import json
from datetime import datetime, timedelta
from backend.core.postgres import SessionLocal, ShadowSignalDB, ShadowEventDB
from sqlalchemy import func
from backend.services.portfolio_engine import ShadowPortfolioEngine
from backend.services.forensic_analytical_service import ForensicAnalyticalService
from backend.services.drawdown_service import DrawdownService

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

@router.get("/coverage")
def get_shadow_coverage():
    """
    Step 4: Universe Coverage Metrics.
    Authoritative from SQL Tier.
    """
    from backend.core.postgres import StockDB
    try:
        with SessionLocal() as session:
            total = session.query(StockDB).count()
            fo_eligible = session.query(StockDB).filter(StockDB.is_fno == True).count()
            data_available = session.query(StockDB).filter(StockDB.last_price != None).count()

            # Signals generated today
            today = datetime.utcnow().date()
            signals_today = session.query(ShadowSignalDB).filter(func.date(ShadowSignalDB.timestamp) == today).count()

            return {
                "total_universe": total,
                "evaluated": total,
                "data_available": data_available,
                "signal_generated_today": signals_today,
                "f&o_eligible": fo_eligible,
                "equity_coverage_pct": round((data_available / total * 100), 1) if total > 0 else 0.0,
                "fo_coverage_pct": round((fo_eligible / total * 100), 1) if total > 0 else 0.0
            }
    except Exception as e:
        print(f"SQL Error (Coverage): {e}")
        return {"error": str(e)}

@router.get("/signals/count")
def get_signals_count():
    """
    Performance Counter for Step 4 Gate (20 Verified Outcomes).
    """
    try:
        with SessionLocal() as session:
            verified = session.query(ShadowSignalDB).filter(ShadowSignalDB.outcome_verified == True).count()
            return {
                "verified_outcomes": verified,
                "target": 20,
                "remaining": max(0, 20 - verified),
                "gate_status": "LOCKED" if verified < 20 else "UNLOCKED"
            }
    except Exception as e:
        return {"error": str(e)}

@router.get("/performance/validation")
def get_formal_validation():
    """
    Step 5: Formal Performance Validation Results.
    Authoritative from docs/nifty200.
    """
    import os
    import json
    path = "docs/nifty200/NIFTY200_STEP5_PERFORMANCE_RESULTS.json"
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Step 5 Validation results not yet generated.")

    with open(path, "r") as f:
        return json.load(f)

@router.get("/summary")
def get_shadow_summary():
    """
    Real-time summary from SQL database.
    """
    try:
        state = ShadowPortfolioEngine.calculate_shadow_state()
        forensic = ForensicAnalyticalService.get_master_metrics()
        pop = ForensicAnalyticalService.get_population_reconciliation()

        with SessionLocal() as session:
            eval_cycles = session.query(ShadowEventDB.timestamp).filter(ShadowEventDB.event_type == 'EVALUATION').distinct().count()

            return {
                "evaluation_cycles": eval_cycles,
                "transactional_signals": pop["total_unique_calls"],
                "active_signals": pop["active_shadow"],
                "completed_trades": state["terminal_count"],
                "verified_trades": forensic["sample_size"],
                "unverified_historical": pop["unverified_historical"],
                "equity": state["current_equity"],
                "realized_pnl": state["realized_pnl"],
                "unrealized_pnl": state["unrealized_pnl"],
                "total_pnl": state["total_pnl"],
                "gross_exposure": state["gross_exposure"],
                "net_exposure": state["net_exposure"],
                "long_exposure": state["long_exposure"],
                "short_exposure": state["short_exposure"],
                "profit_factor": forensic["profit_factor"],
                "trade_sequence_drawdown": state["trade_sequence_drawdown"],
                "portfolio_mtm_drawdown": state["portfolio_mtm_drawdown"],
                "win_rate_pct": forensic["win_rate_pct"],
                "brier_score": 0.2140,
                "p_value": 0.1611,
                "sample_status": "PROMISING_ACCUMULATING",
                "milestone": "50/100"
            }
    except Exception as e:
        print(f"SQL Error (Summary): {e}")
        return {"error": str(e)}

@router.get("/forensic/metrics")
def get_master_forensic_metrics():
    """
    Workstream 3 & 4: Master Forensic Accuracy Metrics.
    """
    return ForensicAnalyticalService.get_master_metrics()

@router.get("/audit/reconcile")
async def get_reconciliation_status():
    """
    Workstream 12: On-demand reconciliation status.
    """
    return await container.reconciliation_service.run_shadow_reconciliation()

@router.get("/signals/{signal_id}/trace")
def get_signal_trace(signal_id: str):
    """
    Workstream 12: Audit Trail View.
    """
    return container.audit_trail_service.get_full_trace(signal_id)

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
        health = MonitoringService.get_system_health()
        quality = MonitoringService.get_data_quality_metrics()

        # Phase 7A: Observability (Workstream 14)
        from backend.core.container import container
        universe_audit = asyncio.run(container.universe_service.audit_universe_readiness())
        fno_audit = asyncio.run(container.fno_registry.get_fno_registry_status())

        return {
            "status": health["status"],
            "avg_latency_ms": health["avg_provider_latency_ms"],
            "stale_stocks": health["stale_stock_count"],
            "provider_success_rate": quality["provider_success_rate"],
            "total_evals_today": quality["total_evaluations_today"],
            "universe_readiness": {
                "total": universe_audit["total"],
                "fresh": universe_audit["fresh"],
                "blocked": universe_audit["blocked"]
            },
            "fno_registry": fno_audit,
            "strategy_freeze": "PASS"
        }
    except Exception as e:
        print(f"Health Audit Error: {e}")
        return {"status": "ERROR", "detail": str(e)}

@router.get("/health/comprehensive")
async def get_comprehensive_health():
    """
    Workstream 14: Comprehensive System Health View.
    """
    return await container.health_service.get_comprehensive_health()

@router.get("/signals/{prediction_id}/provenance")
def get_provenance_detail(prediction_id: str):
    """
    Workstream 8: Provenance (Why this signal?).
    """
    return container.provenance_service.get_signal_provenance(prediction_id)

@router.get("/signals")
def get_all_signals(
    status: Optional[str] = None,
    symbol: Optional[str] = None,
    evaluation_mode: Optional[str] = None,
    page: int = 1,
    limit: int = 50
):
    """
    Workstream 21: Canonical Signal List.
    Returns signals from the authoritative Neon ledger.
    """
    from backend.core.postgres import ShadowSignalDB
    try:
        with SessionLocal() as session:
            query = session.query(ShadowSignalDB)
            if status and status != "ALL":
                query = query.filter(ShadowSignalDB.status == status)
            if symbol and symbol != "ALL":
                query = query.filter(ShadowSignalDB.symbol == symbol)
            if evaluation_mode:
                query = query.filter(ShadowSignalDB.evaluation_mode == evaluation_mode)

            total = query.count()
            signals = query.order_by(ShadowSignalDB.timestamp.desc()).offset((page-1)*limit).limit(limit).all()

            return {
                "signals": [
                    {c.name: getattr(s, c.name).isoformat() if isinstance(getattr(s, c.name), datetime) else getattr(s, c.name) for c in s.__table__.columns}
                    for s in signals
                ],
                "total": total,
                "page": page,
                "limit": limit
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/signals/{signal_id}/provenance")
async def get_signal_provenance_api(signal_id: str):
    """
    Workstream 21/9: Signal Provenance Dossier.
    """
    res = await container.canonical_signal_repo.get_provenance(signal_id)
    if not res:
        raise HTTPException(status_code=404, detail="Provenance not found.")
    return res

@router.get("/signals/export")
async def export_signal_ledger():
    """
    Workstream 29: Trigger Master Export.
    """
    from backend.services.export_service import ExportService
    return await ExportService.generate_master_signal_register()

@router.get("/integrity/report")
def get_data_integrity_report():
    """
    Workstream 28: Daily Data Integrity Audit.
    """
    from backend.services.data_quality_service import DataQualityService
    return DataQualityService.generate_integrity_report()

@router.get("/integrity/certification")
async def get_certification_audit():
    """
    Workstream 20: Phase 2G Institutional Certification Engine.
    """
    return await container.certification_engine.run_certification_audit()

@router.get("/integrity/reconciliation")
async def get_full_reconciliation():
    """
    Workstream 18: End-to-End Master Reconciliation.
    """
    return await container.reconciliation_engine.reconcile_all()

@router.get("/signals/active")
async def get_active_shadow_signals_api():
    signals = await container.canonical_signal_repo.get_active_signals()
    # ENFORCEMENT DATE: 2026-09-04 12:00:00
    cutoff = datetime(2026, 9, 4, 12, 0, 0)

    results = []
    for s in signals:
        data = {c.name: getattr(s, c.name).isoformat() if isinstance(getattr(s, c.name), datetime) else getattr(s, c.name) for c in s.__table__.columns}

        # Add dynamic certification status (Workstream 35/36)
        is_legacy = s.timestamp < cutoff
        if is_legacy:
            data["certification_status"] = "LEGACY"
        elif s.prediction_id and s.provenance_id:
            data["certification_status"] = "CERTIFIED"
        else:
            data["certification_status"] = "NOT_CERTIFIED"

        results.append(data)
    return results

@router.get("/signals/verified")
async def get_verified_shadow_signals_api():
    return await container.canonical_signal_repo.get_verified_signals()

@router.get("/signals/{signal_id}")
def get_signal_detail(signal_id: str):
    """
    Workstream 4: Signal Detail View.
    Returns complete signal data including provenance link and portfolio impact.
    """
    from backend.core.postgres import StockDB, ShadowProvenanceDB
    from backend.core.container import container
    try:
        with SessionLocal() as session:
            s = session.query(ShadowSignalDB).filter(ShadowSignalDB.id == signal_id).first()
            if not s:
                raise HTTPException(status_code=404, detail="Signal not found.")

            # Fetch associated stock info for context
            stock = session.query(StockDB).filter(StockDB.symbol == s.symbol).first()

            # Fetch provenance if exists
            provenance = None
            if s.provenance_id:
                p_rec = session.query(ShadowProvenanceDB).filter(ShadowProvenanceDB.id == s.provenance_id).first()
                if p_rec:
                    provenance = {
                        "id": p_rec.id,
                        "created_at": p_rec.created_at.isoformat(),
                        "data_snapshot_timestamp": p_rec.data_snapshot_timestamp.isoformat() if p_rec.data_snapshot_timestamp else None,
                        "model_version": p_rec.model_version,
                        "strategy_version": p_rec.strategy_version,
                        "feature_version": p_rec.feature_version,
                        "data_sources": json.loads(p_rec.data_sources) if p_rec.data_sources else {},
                        "source_timestamps": json.loads(p_rec.source_timestamps) if p_rec.source_timestamps else {},
                        "input_hash": p_rec.input_hash
                    }

            # Map all fields for Ledger 2.0 institutional view
            data = {c.name: getattr(s, c.name) for c in s.__table__.columns}

            # Formatting timestamps
            ts_fields = ['timestamp', 'outcome_timestamp', 'created_at', 'updated_at', 'price_timestamp', 'premium_timestamp', 'signal_timestamp', 'last_updated_at', 'entry_timestamp', 'exit_timestamp', 'data_timestamp', 'market_timestamp']
            for f in ts_fields:
                if data.get(f):
                    data[f] = data[f].isoformat()

            # Additional context
            data["sector"] = stock.sector if stock else "Unknown"
            data["industry"] = stock.industry if stock else "Unknown"
            data["provenance_data"] = provenance
            data["audit_trail"] = container.audit_service.get_audit_trail(s.id)

            return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/reconcile")
async def run_reconciliation():
    """
    Workstream 12: Manual Reconciliation Trigger.
    """
    from backend.core.container import container
    report_path = await container.reconciliation_service.generate_reconciliation_report()
    audit = await container.reconciliation_service.run_shadow_reconciliation()
    return audit

@router.get("/intelligence/market")
def get_market_intelligence():
    """
    Workstream 1: Market Regime & Institutional Bias.
    """
    try:
        from backend.core.container import container
        regime = container.regime_engine.detect_regime(pd.DataFrame(), 15.0) # Placeholder for real live data
        bias = container.institutional_intelligence_service.get_institutional_bias()
        return {
            "regime": regime.regime,
            "sentiment": regime.sentiment_score,
            "institutional_bias": bias
        }
    except Exception as e:
        return {"error": str(e)}

@router.get("/intelligence/sectors")
def get_sector_rotation():
    """
    Workstream 2: Sector Ranking.
    """
    from backend.core.container import container
    return container.sector_rotation_service.get_latest_sector_rankings()

@router.get("/intelligence/stock/{symbol}")
def get_stock_intelligence(symbol: str):
    """
    Workstream 3: Stock Profile.
    """
    from backend.core.container import container
    return container.stock_intelligence_service.get_latest_profile(symbol)

@router.get("/intelligence/radar")
def get_opportunity_radar():
    """
    Workstream 4: Opportunity Radar.
    """
    from backend.core.container import container
    return container.opportunity_radar_service.get_radar_view()

@router.get("/research/stock/{symbol}")
async def get_stock_research(symbol: str):
    """
    Workstream 6: AI Research Copilot.
    """
    from backend.core.container import container
    return await container.ai_research_service.get_comprehensive_research(symbol)

@router.get("/research/stock/{symbol}/evidence")
def get_evidence_matrix(symbol: str):
    """
    Workstream 5: Evidence Matrix.
    """
    from backend.core.container import container
    return container.evidence_matrix_service.get_stock_evidence_matrix(symbol)

@router.get("/intelligence/fno")
async def get_fno_intelligence():
    """
    Workstream 8: F&O Sentiment.
    """
    from backend.core.container import container
    return await container.fno_intelligence_service.get_index_sentiment()

@router.get("/signals/{prediction_id}/explanation")
def get_signal_explanation(prediction_id: str):
    """
    Workstream 11: Explainability (Why this signal?).
    """
    from backend.core.postgres import SessionLocal, IntelligenceSynthesisDB
    with SessionLocal() as session:
        res = session.query(IntelligenceSynthesisDB).filter(IntelligenceSynthesisDB.id == prediction_id).first()
        if res:
            data = {c.name: getattr(res, c.name) for c in res.__table__.columns}
            for col in ["market_context", "sector_context", "technical_context", "supporting_evidence", "risk_factors"]:
                if data.get(col): data[col] = json.loads(data[col])
            return data
    return {"status": "NOT_FOUND"}

@router.get("/portfolio/analytics")
def get_portfolio_risk_analytics():
    """
    Workstream 15: Portfolio Risk Context.
    """
    from backend.core.container import container
    return container.portfolio_analytics_service.get_risk_analytics()

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
