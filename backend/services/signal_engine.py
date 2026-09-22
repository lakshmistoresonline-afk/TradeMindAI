from typing import List, Dict, Any, Optional
import datetime
from datetime import timezone
import uuid

import json
import hashlib
from backend.domain.models.ios import LiveSignal, SignalEvent
from backend.services.regime_engine import MarketRegimeEngine
from backend.services.risk_engine import RiskEngine
from backend.services.calibration_service import CalibrationService
from backend.services.signal_quality_service import SignalQualityService
from backend.services.signal_validator_service import SignalValidatorService
from backend.core.container import container
from backend.domain.models.data_platform import ModelMetadata

class SignalEngine:
    @staticmethod
    async def generate_signal(
        symbol: str,
        asset_class: str,
        timeframe: str,
        stock: Optional[Any] = None,
        features_list: Optional[List[Any]] = None,
        current_dd: Optional[float] = None,
        champion: Optional[ModelMetadata] = None,
        save_prediction: bool = True,
        evaluation_timestamp: Optional[datetime.datetime] = None
    ) -> Optional[LiveSignal]:
        """
        Master Signal Generation Node.
        Implements No-Trade Engine and Probability Calibration.
        Vision 2.3: Shadow Mode & Instrumentation Hardening.
        """
        # Execution time context
        eval_time = evaluation_timestamp or datetime.datetime.now(timezone.utc)

        # 1. Fetch Fresh Data (if not provided)
        if stock is None:
            stock = await container.repository.get_stock_by_symbol(symbol)
        if not stock:
            return None

        # 2. Extract Features (Time-Safe) (if not provided)
        if features_list is None:
            features_list = await container.data_platform_repo.get_features_by_range(
                symbol,
                eval_time - datetime.timedelta(days=14),
                eval_time
            )
        if not features_list:
            return None
        last_features = features_list[-1].features

        # 3. Model Inference (Champion Model specialized for timeframe/horizon)
        ml_res = await container.ml_service.predict_with_champion(
            symbol,
            last_features,
            horizon=timeframe,
            champion=champion,
            save=save_prediction
        )

        # 3.5 Extract Probabilities with Forensic Safety
        ml_metadata = ml_res.get("metadata", {})
        if "calibrated_probability_up" not in ml_metadata or "raw_probability_up" not in ml_metadata:
            print(f"   [FORENSIC_FAIL] {symbol} Aborting: Missing ML metadata (Probabilities).")
            return None

        prob_up = ml_metadata["calibrated_probability_up"]
        raw_prob_up = ml_metadata["raw_probability_up"]

        # 4. Map to Direction Probability
        direction = "LONG" if ml_res.get("prediction") == "UP" else "SHORT"
        calibrated_prob = CalibrationService.get_direction_probability(prob_up, direction)
        raw_prob = CalibrationService.get_direction_probability(raw_prob_up, direction)

        # 5. REGIME ANALYSIS (Passed to Risk Engine & Gates)
        regime_obj = await container.ios_repo.get_latest_regime()
        if not regime_obj:
            print(f"   [FORENSIC_FAIL] {symbol} Aborting: Missing Market Regime context.")
            return None

        regime_label = regime_obj.regime
        regime_prob = regime_obj.sentiment_score

        # 6. Risk Calculation (Master Node - Regime Aware)
        price = last_features.get("Close") or last_features.get("close") or (stock.last_price if not evaluation_timestamp else 0.0)

        import math
        if not price or not math.isfinite(price):
            print(f"   [!] {symbol} Invalid price: {price}")
            return None

        atr = last_features.get("ATR") or last_features.get("Atr")
        if not atr or not math.isfinite(atr) or atr <= 0:
            print(f"   [FORENSIC_FAIL] {symbol} Aborting: Missing/Invalid ATR data.")
            return None

        risk_params = RiskEngine.calculate_trade_parameters(
            symbol, price,
            direction,
            atr,
            horizon=timeframe,
            regime=regime_label
        )

        if not risk_params: return None

        # 7. EXPECTED VALUE
        reward_amt = abs(risk_params["target"] - price)
        risk_amt = abs(price - risk_params["stop_loss"])

        expected_val = CalibrationService.calculate_expected_value(
            calibrated_prob,
            reward_amt,
            risk_amt,
            entry_price=price
        )

        if not math.isfinite(expected_val):
            expected_val = 0.0

        # 8. PRODUCTION RISK GATES (V2.2)
        rejection_reason = None

        if current_dd is None:
            current_dd = 0.0

        # B. Data Freshness Gate
        last_feature_date = features_list[-1].date
        if last_feature_date.tzinfo is None:
             last_feature_date = last_feature_date.replace(tzinfo=timezone.utc)

        if (eval_time - last_feature_date).total_seconds() > 432000:
            rejection_reason = "STALE_MARKET_DATA"

        # C. Liquidity Gate
        if stock.avg_volume and stock.avg_volume < 10_000_000:
            rejection_reason = "INSUFFICIENT_LIQUIDITY"

        # Attach sector bias context
        from backend.services.sector_rotation_service import SectorRotationService
        sec_info = SectorRotationService.get_stock_sector_bias(getattr(stock, "sector", None))
        last_features["sector_bias"] = sec_info.get("bias", "NEUTRAL")
        last_features["sector_rank"] = sec_info.get("rank", 5)

        # D. Trend Alignment Filter
        ema200 = last_features.get("ema_200", price)
        if not rejection_reason:
            if direction == "LONG" and price < ema200: rejection_reason = "TREND_CONFLICT_BEARISH"
            elif direction == "SHORT" and price > ema200: rejection_reason = "TREND_CONFLICT_BULLISH"

        # E. Breakout Magnitude Filter
        if not rejection_reason:
            avg_price = last_features.get("sma_20", price)
            magnitude = abs(price - avg_price)
            if magnitude < (atr * 0.5): rejection_reason = "INSIGNIFICANT_MOMENTUM"

        # F. Probability & EV Gates
        if not rejection_reason:
            if reward_amt <= 0 or risk_amt <= 0: rejection_reason = "INVALID_GEOMETRY"
            elif calibrated_prob < 0.52: rejection_reason = "WEAK_EDGE"
            elif expected_val <= 0: rejection_reason = "NEGATIVE_EXPECTANCY"
            elif risk_params["risk_pct"] > 12: rejection_reason = "EXCESSIVE_VOLATILITY"
            elif regime_label == "HIGH_VOLATILITY" and calibrated_prob < 0.65: rejection_reason = "REGIME_CONFLICT"

        if rejection_reason:
            print(f"   [NO_TRADE] {symbol} rejected: {rejection_reason} (Prob: {calibrated_prob:.4f}, EV: {expected_val:.4f})")
            return None

        # 8.5 QUALITY GATE (V2.2)
        champion_model = champion or await container.data_platform_repo.get_champion_model(symbol, horizon=timeframe)
        if not SignalQualityService.should_publish(timeframe, champion_model, calibrated_prob):
            print(f"   [QUALITY_GATE] {symbol} ({timeframe}) failed hard gate.")
            return None

        quality_class = SignalQualityService.get_quality_class(timeframe, champion_model)

        # 9. DATA QUALITY SCORE
        data_ts = features_list[-1].date
        if data_ts.tzinfo is None:
             data_ts = data_ts.replace(tzinfo=timezone.utc)

        staleness = (eval_time - data_ts).total_seconds() / 3600.0 # hours

        recent_prices = await container.repository.get_recent_prices(symbol, limit=20)
        coverage_score = min(1.0, len(recent_prices) / 20.0)
        freshness_score = max(0.0, 1.0 - (staleness / 24.0))
        data_quality = (freshness_score * 0.7) + (coverage_score * 0.3)

        eligibility = "ELIGIBLE"
        if staleness > 24:
            eligibility = "STALE_DATA"
        elif coverage_score < 0.5:
            eligibility = "DATA_BLOCKED"

        # 10. V2.3 SHADOW ARCHITECTURE (Workstream 11)
        # 10.1 Persist Prediction
        from backend.domain.models.data_platform import Prediction
        pred_id = str(uuid.uuid4())
        diag_provenance = {
            "predicted_probability": float(calibrated_prob),
            "predicted_EV": float(expected_val),
            "predicted_RR": float(risk_params["risk_reward"]),
            "market_regime": regime_label
        }

        prediction_obj = Prediction(
            id=pred_id,
            symbol=symbol,
            timestamp=eval_time,
            model_version=ml_res.get("model_version", "TradeMind Core v2.2"),
            feature_version="v1.0.0",
            prediction="UP" if direction == "LONG" else "DOWN",
            probability=float(calibrated_prob),
            expected_value=float(expected_val),
            direction=direction,
            confidence=float(calibrated_prob),
            regime=regime_label,
            metadata=diag_provenance,
            created_at=datetime.datetime.now(timezone.utc)
        )
        await container.data_platform_repo.save_prediction(prediction_obj)

        # 10.2 Generate Provenance Record
        provenance_id = str(uuid.uuid4())
        feat_str = json.dumps(last_features, sort_keys=True)
        res_str = json.dumps(ml_res, sort_keys=True, default=str)
        provenance_data = {
            "provenance_id": provenance_id,
            "data_snapshot_timestamp": data_ts,
            "model_version": ml_res.get("model_version", "TradeMind Core v2.2"),
            "strategy_version": "v2.2",
            "feature_version": "v1.0.0",
            "data_sources": {"price": "YFinance_Canonical", "indicators": "DuckDB-TA"},
            "source_timestamps": {"market_data": data_ts.isoformat()},
            "input_hash": hashlib.sha256(feat_str.encode()).hexdigest(),
            "output_hash": hashlib.sha256(res_str.encode()).hexdigest(),
        }

        # 10.3 Instrumentation Context (Phase 8 & 9)
        candidate_id = f"cand_{symbol}_{timeframe}_{eval_time.strftime('%Y%m%d%H%M')}"
        regime_meta = {
            "regime": regime_label,
            "regime_timestamp": regime_obj.date if hasattr(regime_obj, 'date') else eval_time,
            "regime_source": "Institutional_Regime_Engine",
            "regime_confidence": regime_obj.sentiment_score,
            "regime_available": True
        }

        # 10.4 V2.2 Publication Gate
        # Every signal must be checked against the official SignalValidatorService
        # signal_dict_pre is used to create a temp LiveSignal for validation
        signal_dict_pre = {
            "id": f"sig_{symbol}_{timeframe}_{eval_time.strftime('%Y%m%d%H%M')}",
            "symbol": symbol,
            "direction": direction,
            "timeframe": timeframe,
            "entry_price": price,
            "target_price": risk_params["target"],
            "stop_price": risk_params["stop_loss"],
            "conviction": float(calibrated_prob * 100),
            "data_timestamp": data_ts,
            "provenance_id": provenance_id,
            "candidate_timestamp": eval_time,
            "price_at_signal": price,
            "status": "WAITING_FOR_ENTRY",
            **regime_meta
        }

        v22_valid = SignalValidatorService.validate_publication(LiveSignal(**signal_dict_pre))

        # 10.5 V2.3 Shadow Gate (Phase 1 Isolation)
        from backend.services.signal_quality_gate import SignalQualityGate
        from backend.services.signal_shadow_service import SignalShadowService

        v23_gate_res = {"decision": "NO_SIGNAL", "reasons": ["SHADOW_ERROR"], "metadata": {}}
        try:
            v23_gate_res = SignalQualityGate.evaluate_v23_gate(
                LiveSignal(**signal_dict_pre),
                last_features
            )
        except Exception as ge:
            print(f"[Shadow] Gate Error: {ge}")

        candidate_data = {
            "candidate_id": candidate_id, "symbol": symbol, "price": price,
            "eval_time": eval_time, "regime_label": regime_label, "data_status": eligibility,
            "calibrated_prob": calibrated_prob, "expected_val": expected_val
        }

        if not v22_valid["is_valid"]:
            print(f"   [GATE_REJECTED] {symbol} failed production V2.2 audit: {v22_valid['issues']}")
            try:
                await SignalShadowService.record_shadow_decision(None, v23_gate_res, candidate_data)
            except Exception as se:
                print(f"[Shadow] Failsafe (NO_SIGNAL): {se}")
            return None

        # 11. Final V2.2 Production Signal
        from backend.core.config import settings
        eval_mode = "LIVE_SHADOW" if settings.ENVIRONMENT in ["production", "shadow"] else "TEST"

        v22_signal = LiveSignal(
            id=f"sig_{symbol}_{timeframe}_{eval_time.strftime('%Y%m%d%H%M')}",
            symbol=symbol,
            company_name=stock.name if hasattr(stock, 'name') else f"{symbol} Limited",
            isin=stock.isin if hasattr(stock, 'isin') else None,
            exchange="NSE",
            asset_type="EQUITY",
            instrument_id=stock.instrument_id if hasattr(stock, 'instrument_id') else f"NSE_{symbol}",
            instrument_type="EQUITY",
            direction=direction,
            rating="BUY" if direction == "LONG" else "SELL",
            timeframe=timeframe,
            strategy_version="v2.2",
            signal_version="1.0",
            timestamp=eval_time,
            valid_until=eval_time + datetime.timedelta(days={"SWING": 30, "SHORT": 7, "INTRADAY": 1, "LONG": 365}.get(timeframe, 30)),

            # Price
            entry_price=price,
            entry_zone_low=price * 0.995,
            entry_zone_high=price * 1.005,
            target_price=risk_params["target"],
            stop_price=risk_params["stop_loss"],
            current_price=price,
            current_price_source="YFinance_Live",
            current_price_timestamp=eval_time,
            current_price_status="FRESH",

            # Phase 8: Instrumentation
            candidate_timestamp=eval_time,
            published_at=datetime.datetime.now(timezone.utc),
            price_at_signal=price,
            price_at_publish=price,

            # Risk
            risk_amount=3.0,
            risk_amount_abs=risk_amt,
            reward_amount_abs=reward_amt,
            risk_reward_ratio=float(risk_params["risk_reward"]),

            # Intelligence
            raw_probability=float(raw_prob),
            calibrated_probability=float(calibrated_prob),
            expected_value=float(expected_val),
            opportunity_score=float(calibrated_prob * 100),
            confidence=float(calibrated_prob),
            signal_score=float(expected_val),
            # Phase 9: Regime Instrumentation
            **regime_meta,
            regime_probability=float(regime_prob),

            # Lineage
            model_id=ml_res.get("model_id", f"mod_{symbol}_v2.2"),
            model_version=ml_res.get("model_version", "TradeMind Core v2.2"),
            model_hash=ml_res.get("model_hash"),
            model_run_id=f"run_{ml_res.get('model_version')}",
            feature_snapshot_id=f"feat_snap_{symbol}_{eval_time.strftime('%Y%m%d%H%M')}",
            feature_version="v1.0.0",
            feature_hash=hashlib.sha256(feat_str.encode()).hexdigest(),
            prediction_id=pred_id,
            prediction_timestamp=eval_time,
            model_timestamp=eval_time,
            feature_timestamp=data_ts,
            decision_timestamp=eval_time,
            provenance_id=provenance_id,
            provenance=provenance_data,
            data_source="YFinance_Canonical",
            data_source_timestamp=data_ts,
            dataset_id="NIFTY_200_AUG2026",
            dataset_hash=hashlib.sha256(symbol.encode()).hexdigest(),

            # Lifecycle
            status="WAITING_FOR_ENTRY",
            lifecycle_state="CREATED",
            activated_at=eval_time,
            updated_at=datetime.datetime.now(timezone.utc),

            # Quality
            quality_class=quality_class,
            data_quality_status="FRESH" if staleness < 24 else "STALE",
            validation_status="CERTIFIED",
            audit_status="PENDING",
            deployment_sha=settings.GIT_SHA,

            # Legacy/Internal
            conviction=float(calibrated_prob * 100),
            asset_class="EQUITY",
            underlying_symbol=None,
            quantity=1,
            capital_allocation=100000.0,
            signal_eligibility=eligibility,
            evaluation_mode=eval_mode,
            universe_version="NIFTY_200_AUG2026",
            data_timestamp=data_ts,
            market_timestamp=eval_time,
            outcome_verified=False,
            events=[SignalEvent(type="GENERATED", message="Passed forensic P0 risk/edge audit.")],
            mfe=0.0,
            mae=0.0
        )

        # Record Shadow Decision for V2.3 (Phase 1 Isolation)
        try:
            await SignalShadowService.record_shadow_decision(v22_signal, v23_gate_res, candidate_data)
        except Exception as se:
            print(f"[Shadow] Failsafe: Shadow recording failed but V2.2 production proceeds: {se}")

        return v22_signal
