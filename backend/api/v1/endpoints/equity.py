from fastapi import APIRouter, HTTPException, Query, Depends
from backend.core.auth import get_current_user
from typing import List, Dict, Any, Optional
from sqlalchemy import func, or_, and_
from backend.core.container import container
from backend.domain.models.ios import LiveSignal
from backend.services.signal_ledger_service import SignalLedgerService
from backend.services.signal_lifecycle_service import SignalLifecycleService
from backend.services.research_metrics_service import ResearchMetricsService
from backend.services.forensic_analytical_service import ForensicAnalyticalService
from fastapi_cache.decorator import cache
import datetime
import json
import math

try:
    from sklearn.metrics import roc_auc_score
except ImportError:
    roc_auc_score = None

router = APIRouter()

def is_eligible_buy(obj: Any) -> bool:
    """
    Canonical BUY eligibility predicate.
    Validates direction, rating, and signal_rating independently.
    Rejects missing, unknown, conflicting, SELL, or SHORT values.
    """
    if not obj:
        return False

    direction = getattr(obj, "direction", None) or (obj.get("direction") if isinstance(obj, dict) else None)
    rating = getattr(obj, "rating", None) or (obj.get("rating") if isinstance(obj, dict) else None)
    signal_rating = getattr(obj, "signal_rating", None) or (obj.get("signal_rating") if isinstance(obj, dict) else None)

    if not direction:
        return False

    dir_upper = str(direction).upper()
    if dir_upper != "LONG":
        return False

    ratings_to_check = []
    if rating is not None:
        ratings_to_check.append(str(rating).upper())
    if signal_rating is not None:
        ratings_to_check.append(str(signal_rating).upper())

    if not ratings_to_check:
        return False

    for r in ratings_to_check:
        if "SELL" in r or "SHORT" in r or r not in ("BUY", "STRONG_BUY"):
            return False

    return True

def calculate_auc_with_ties(y_true: List[float], y_prob: List[float]) -> Optional[float]:
    """
    Calculates Wilcoxon-Mann-Whitney AUC with proper average rank correction for ties.
    Requirements:
    1. Reject mismatched array lengths and insufficient sample sizes (< 2).
    2. Reject invalid labels, non-numeric probabilities, NaN, infinity, and probabilities outside [0, 1].
    3. Return None when valid observations do not contain both outcome classes.
    4. Return 0.5 for tied scores when both classes are present.
    5. Preserve correct average-rank tie handling in manual fallback.
    """
    if not y_true or not y_prob or len(y_true) != len(y_prob) or len(y_true) < 2:
        return None

    for y, p in zip(y_true, y_prob):
        if y not in (0.0, 1.0):
            return None
        if p is None or not isinstance(p, (int, float)) or not math.isfinite(p) or not (0.0 <= p <= 1.0):
            return None

    n1 = sum(1 for y in y_true if y == 1.0)
    n0 = sum(1 for y in y_true if y == 0.0)
    if n1 == 0 or n0 == 0:
        return None

    if len(set(y_prob)) <= 1:
        return 0.5

    if roc_auc_score is not None:
        try:
            return round(float(roc_auc_score(y_true, y_prob)), 3)
        except Exception:
            pass

    indexed = sorted(enumerate(zip(y_prob, y_true)), key=lambda x: x[1][0])
    ranks = [0.0] * len(y_true)
    i = 0
    while i < len(indexed):
        j = i
        while j < len(indexed) and indexed[j][1][0] == indexed[i][1][0]:
            j += 1
        avg_rank = (i + 1 + j) / 2.0
        for k in range(i, j):
            ranks[indexed[k][0]] = avg_rank
        i = j

    sum_ranks_pos = sum(ranks[idx] for idx, (_, y) in enumerate(zip(y_prob, y_true)) if y == 1.0)
    u = sum_ranks_pos - (n1 * (n1 + 1)) / 2.0
    return round(u / (n1 * n0), 3)

@router.get("/signals", response_model=List[LiveSignal])
async def get_equity_signals(
    status: Optional[str] = None,
    symbol: Optional[str] = None,
    limit: int = Query(500, le=1000)
):
    """
    Returns complete authoritative BUY-only signal records from PostgreSQL ledger.
    """
    try:
        from backend.core.postgres import SessionLocal, LiveSignalDB
        with SessionLocal() as session:
            db_signals = session.query(LiveSignalDB).order_by(LiveSignalDB.timestamp.desc()).all()
            eligible = [s for s in db_signals if is_eligible_buy(s)]

            if status:
                eligible = [s for s in eligible if s.status == status]
            if symbol:
                eligible = [s for s in eligible if s.symbol.upper() == symbol.upper()]

            return [container.ios_repo._map_db_to_live_signal(s) for s in eligible[:limit]]
    except Exception as e:
        print(f"Postgres signal fetch error: {e}")
        raise HTTPException(status_code=503, detail="Authoritative signal ledger temporarily unavailable.")

@router.get("/signals/{signal_id}", response_model=LiveSignal)
async def get_signal_detail(signal_id: str):
    signal = await SignalLedgerService.get_signal(signal_id)
    if not signal or not is_eligible_buy(signal):
        raise HTTPException(status_code=404, detail="Signal not found or not eligible")
    return signal

@router.get("/signals/{signal_id}/explanation")
def get_signal_explanation(signal_id: str):
    """
    Explainability (Why this signal?).
    """
    from backend.core.postgres import SessionLocal, IntelligenceSynthesisDB, ShadowSignalDB
    with SessionLocal() as session:
        sig = session.query(ShadowSignalDB).filter(ShadowSignalDB.id == signal_id).first()
        if not sig or not is_eligible_buy(sig):
            raise HTTPException(status_code=404, detail="Signal not found or not eligible")

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
    Returns rigorous accuracy forensics calculated strictly from genuine persisted predictions and resolved outcomes.
    Enforces strict status rules: INSUFFICIENT_EVIDENCE, PARTIALLY_VERIFIED, VERIFIED based on coverage & AUC.
    """
    horizons_report = {}
    try:
        from backend.core.postgres import SessionLocal, ShadowSignalDB
        with SessionLocal() as session:
            for h_name in ["SHORT", "SWING", "LONG"]:
                all_records = session.query(ShadowSignalDB).filter(
                    ShadowSignalDB.status.in_(["TARGET_HIT", "STOP_LOSS", "EXPIRED"]),
                    ShadowSignalDB.signal_type == h_name
                ).all()

                eligible_records = [r for r in all_records if is_eligible_buy(r)]
                total_resolved_outcomes = len(eligible_records)

                directional_outcomes = [s for s in eligible_records if s.status in ["TARGET_HIT", "STOP_LOSS"]]
                eligible_count = len(directional_outcomes)

                if eligible_count == 0:
                    horizons_report[h_name] = {
                        "sample_size": total_resolved_outcomes,
                        "total_resolved_outcomes": total_resolved_outcomes,
                        "eligible_directional_outcomes": 0,
                        "valid_prediction_pairs": 0,
                        "prediction_coverage": 0.0,
                        "auc": None,
                        "win_rate": None,
                        "brier": None,
                        "logloss": None,
                        "ece": None,
                        "status": "INSUFFICIENT_EVIDENCE",
                        "reason": "No eligible directional resolved outcomes (TARGET_HIT / STOP_LOSS) found for this horizon."
                    }
                    continue

                wins = sum(1 for s in directional_outcomes if s.status == "TARGET_HIT")
                win_rate = round(wins / eligible_count * 100.0, 2)

                brier_total = 0.0
                logloss_total = 0.0
                valid_pairs_count = 0
                bins = [[] for _ in range(10)]
                y_true = []
                y_prob = []
                EPS = 1e-15

                for s in directional_outcomes:
                    prob = s.calibrated_probability if s.calibrated_probability is not None else s.raw_probability
                    if prob is not None and isinstance(prob, (int, float)) and math.isfinite(prob) and 0.0 <= prob <= 1.0:
                        actual = 1.0 if s.status == "TARGET_HIT" else 0.0
                        brier_total += (prob - actual) ** 2

                        p_clamped = max(EPS, min(1.0 - EPS, prob))
                        logloss_total += - (actual * math.log(p_clamped) + (1.0 - actual) * math.log(1.0 - p_clamped))

                        bin_idx = min(9, int(prob * 10))
                        bins[bin_idx].append((prob, actual))
                        y_true.append(actual)
                        y_prob.append(prob)
                        valid_pairs_count += 1

                prediction_coverage = round(valid_pairs_count / eligible_count, 4) if eligible_count > 0 else 0.0

                if valid_pairs_count == 0:
                    horizons_report[h_name] = {
                        "sample_size": total_resolved_outcomes,
                        "total_resolved_outcomes": total_resolved_outcomes,
                        "eligible_directional_outcomes": eligible_count,
                        "valid_prediction_pairs": 0,
                        "prediction_coverage": prediction_coverage,
                        "auc": None,
                        "win_rate": win_rate,
                        "brier": None,
                        "logloss": None,
                        "ece": None,
                        "status": "INSUFFICIENT_EVIDENCE",
                        "reason": "Resolved outcomes present but missing valid finite prediction probabilities in [0, 1]."
                    }
                    continue

                brier_score = round(brier_total / valid_pairs_count, 4)
                logloss = round(logloss_total / valid_pairs_count, 4)

                ece_total = 0.0
                for b in bins:
                    if len(b) > 0:
                        b_acc = sum(act for _, act in b) / len(b)
                        b_conf = sum(pr for pr, _ in b) / len(b)
                        ece_total += (len(b) / valid_pairs_count) * abs(b_acc - b_conf)
                ece = round(ece_total, 4)

                auc = calculate_auc_with_ties(y_true, y_prob)

                # Strict status assignment rules:
                # - INSUFFICIENT_EVIDENCE: if eligible_count == 0 or valid_pairs_count == 0
                # - PARTIALLY_VERIFIED: if auc is None or prediction_coverage < 1.0
                # - VERIFIED: only when auc is not None and prediction_coverage == 1.0
                if auc is None or prediction_coverage < 1.0:
                    horizon_status = "PARTIALLY_VERIFIED"
                    reason = "AUC uncomputable or prediction coverage incomplete (< 100%)." if auc is None else "Prediction coverage incomplete (< 100%)."
                else:
                    horizon_status = "VERIFIED"
                    reason = None

                horizons_report[h_name] = {
                    "sample_size": total_resolved_outcomes,
                    "total_resolved_outcomes": total_resolved_outcomes,
                    "eligible_directional_outcomes": eligible_count,
                    "valid_prediction_pairs": valid_pairs_count,
                    "prediction_coverage": prediction_coverage,
                    "auc": auc,
                    "win_rate": win_rate,
                    "brier": brier_score,
                    "logloss": logloss,
                    "ece": ece,
                    "status": horizon_status,
                    "reason": reason
                }
    except Exception as e:
        print(f"Accuracy report error: {e}")
        raise HTTPException(status_code=503, detail="Authoritative accuracy ledger temporarily unavailable.")

    perf = await get_equity_performance()

    has_fully_verified_horizon = any(h.get("status") == "VERIFIED" for h in horizons_report.values())
    has_partially_verified = any(h.get("status") == "PARTIALLY_VERIFIED" for h in horizons_report.values())

    if has_fully_verified_horizon and perf.get("status") == "VERIFIED":
        benchmark_status = "VERIFIED"
    elif has_fully_verified_horizon or has_partially_verified or perf.get("status") == "VERIFIED":
        benchmark_status = "PARTIALLY_VERIFIED"
    else:
        benchmark_status = "INSUFFICIENT_EVIDENCE"

    return {
        "horizons": horizons_report,
        "verified_benchmark": {
            "n": perf.get("sample_size", 0),
            "win_rate": perf.get("win_rate"),
            "profit_factor": perf.get("profit_factor"),
            "net_pnl": perf.get("net_pnl"),
            "status": benchmark_status
        }
    }

@router.get("/performance")
async def get_equity_performance():
    """
    Returns performance metrics calculated strictly from canonical persisted resolved BUY signal ledger outcomes.
    """
    try:
        from backend.core.postgres import SessionLocal, ShadowSignalDB
        with SessionLocal() as session:
            all_resolved = session.query(ShadowSignalDB).filter(
                ShadowSignalDB.status.in_(["TARGET_HIT", "STOP_LOSS", "EXPIRED"])
            ).all()

            resolved = [r for r in all_resolved if is_eligible_buy(r)]
            if not resolved:
                return {
                    "sample_size": 0,
                    "wins": 0,
                    "losses": 0,
                    "win_rate": None,
                    "profit_factor": None,
                    "expectancy": None,
                    "net_pnl": None,
                    "brier_score": None,
                    "status": "INSUFFICIENT_EVIDENCE",
                    "reason": "Ledger is reachable but contains no eligible resolved BUY records."
                }

            signals_data = [{c.name: getattr(s, c.name) for c in s.__table__.columns} for s in resolved]
            metrics = ResearchMetricsService.calculate_performance_metrics(signals_data)
            return metrics
    except Exception as e:
        print(f"Performance calculation error: {e}")
        raise HTTPException(status_code=503, detail="Authoritative performance ledger temporarily unavailable.")

@router.get("/market")
@cache(expire=300)
async def get_market_state():
    from backend.services.market_data_service import MarketDataService
    return await MarketDataService.get_market_state()

@router.get("/status")
def get_strategy_status():
    from backend.services.market_calendar import MarketCalendar
    from backend.core.config import settings

    return {
        "strategy": "trademind-equity-v2.2",
        "universe": "NIFTY 500",
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
    page: int = Query(1, ge=1),
    limit: int = Query(500, ge=1, le=1000),
    user: dict = Depends(get_current_user)
):
    """
    Returns 1-Year historical signal records from the shadow_signals ledger (strictly BUY-only).
    Preserves source direction without unconditional overwrites.
    """
    from backend.core.postgres import SessionLocal, ShadowSignalDB
    with SessionLocal() as session:
        all_records = session.query(ShadowSignalDB).filter(
            ShadowSignalDB.status != "ACTIVE"
        ).all()

        eligible_records = [r for r in all_records if is_eligible_buy(r)]

        one_year_ago = datetime.datetime.utcnow() - datetime.timedelta(days=365)
        one_year_records = [r for r in eligible_records if r.created_at and r.created_at >= one_year_ago]

        target_hits_1y = sum(1 for r in one_year_records if r.status == "TARGET_HIT")
        stop_losses_1y = sum(1 for r in one_year_records if r.status == "STOP_LOSS")
        expired_1y = sum(1 for r in one_year_records if r.status == "EXPIRED")
        total_1y = len(one_year_records)

        filtered = one_year_records
        if symbol and symbol != "ALL":
            sym_upper = symbol.upper()
            filtered = [r for r in filtered if r.symbol and (sym_upper in r.symbol.upper() or sym_upper in r.id.upper())]
        if horizon and horizon != "ALL":
            filtered = [r for r in filtered if (r.signal_type == horizon or r.timeframe == horizon)]
        if quality and quality != "ALL":
            filtered = [r for r in filtered if r.quality_class == quality]
        if status and status != "ALL":
            filtered = [r for r in filtered if r.status == status]

        filtered_total = len(filtered)

        offset = (page - 1) * limit
        paged_records = filtered[offset:offset + limit]

        results = []
        for s in paged_records:
            data = {c.name: getattr(s, c.name) for c in s.__table__.columns}
            for k, v in data.items():
                if isinstance(v, datetime.datetime): data[k] = v.isoformat()
            data["timeframe"] = data.get("signal_type") or data.get("timeframe") or "SWING"
            # Preserve stored direction unchanged
            data["direction"] = s.direction
            results.append(data)

        return {
            "records": results,
            "total": filtered_total,
            "summary": {
                "total": total_1y,
                "target_hits": target_hits_1y,
                "stop_losses": stop_losses_1y,
                "expired": expired_1y
            }
        }

@router.get("/signals/{signal_id}/forensics")
async def get_signal_forensics(signal_id: str):
    """
    Forensic Reconstruction (Phase 4).
    Reconstructs complete timeline and evidence for a specific signal.
    """
    signal = await SignalLedgerService.get_signal(signal_id)
    if not signal or not is_eligible_buy(signal):
        raise HTTPException(status_code=404, detail="Signal not found or not eligible")

    provenance = await container.ios_repo.get_signal_provenance(signal_id)
    explanation = get_signal_explanation(signal_id)

    return {
        "signal": signal,
        "provenance": provenance,
        "explanation": explanation,
        "identity": {
            "deployment_sha": signal.deployment_sha,
            "strategy_version": signal.strategy_version,
            "model_version": signal.model_version
        },
        "verification": {
            "is_verified": signal.outcome_verified,
            "outcome": signal.outcome,
            "exit_reason": signal.exit_reason
        }
    }

@router.get("/features/{symbol}")
async def get_equity_features(symbol: str, limit: int = 30):
    """
    GET /api/v1/equity/features/{symbol}
    Returns technical features for the given symbol from the database.
    """
    from backend.core.postgres import SessionLocal, TechnicalFeatureDB
    with SessionLocal() as session:
        feats = session.query(TechnicalFeatureDB).filter(
            TechnicalFeatureDB.symbol == symbol.upper()
        ).order_by(TechnicalFeatureDB.timestamp.desc()).limit(limit).all()

        results = []
        for f in feats:
            data = {c.name: getattr(f, c.name) for c in f.__table__.columns}
            if isinstance(data.get("timestamp"), datetime.datetime):
                data["timestamp"] = data["timestamp"].isoformat()
            if isinstance(data.get("calculated_at"), datetime.datetime):
                data["calculated_at"] = data["calculated_at"].isoformat()
            results.append(data)
        return results
