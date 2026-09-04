from typing import List, Dict, Any, Optional
import datetime
import uuid
from backend.domain.models.ios import LiveSignal, SignalEvent
from backend.services.regime_engine import MarketRegimeEngine
from backend.services.risk_engine import RiskEngine
from backend.services.calibration_service import CalibrationService
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
        save_prediction: bool = True
    ) -> Optional[LiveSignal]:
        """
        Master Signal Generation Node.
        Implements No-Trade Engine and Probability Calibration.
        Optimized for bulk scans by accepting pre-fetched data.
        """
        # 1. Fetch Fresh Data (if not provided)
        if stock is None:
            stock = await container.repository.get_stock_by_symbol(symbol)
        if not stock: return None

        # 2. Extract Features (Time-Safe) (if not provided)
        if features_list is None:
            features_list = await container.data_platform_repo.get_features_by_range(
                symbol,
                datetime.datetime.utcnow() - datetime.timedelta(days=7),
                datetime.datetime.utcnow()
            )
        if not features_list: return None
        last_features = features_list[-1].features

        # 3. Model Inference (Champion Model)
        # Refactored to accept pre-loaded champion and control persistence
        ml_res = await container.ml_service.predict_with_champion(
            symbol,
            last_features,
            champion=champion,
            save=save_prediction
        )

        # Calibration is now integrated into predict_with_champion (Platt Scaling)
        # We use the raw probability for metadata and the calibrated for decision logic.
        prob_up = ml_res.get("metadata", {}).get("calibrated_probability_up", 0.5)
        raw_prob_up = ml_res.get("metadata", {}).get("raw_probability_up", 0.5)

        # 4. Map to Direction Probability
        direction = "LONG" if ml_res.get("prediction") == "UP" else "SHORT"
        calibrated_prob = CalibrationService.get_direction_probability(prob_up, direction)
        raw_prob = CalibrationService.get_direction_probability(raw_prob_up, direction)

        # 5. Risk Calculation (Master Node)
        price = stock.last_price or 0.0
        atr = last_features.get("ATR") or last_features.get("Atr") or (price * 0.02)
        risk_params = RiskEngine.calculate_trade_parameters(
            symbol, price,
            direction,
            atr
        )

        if not risk_params: return None

        # P1 Optimization: Override to proven 3%/3% fixed target/stop for SWING
        # (Based on EXP001 Research)
        risk_params["target"] = price * (1.03 if direction == "LONG" else 0.97)
        risk_params["stop_loss"] = price * (0.97 if direction == "LONG" else 1.03)
        risk_params["risk_reward"] = 1.0

        # 6. EXPECTED VALUE
        reward_amt = abs(risk_params["target"] - price)
        risk_amt = abs(price - risk_params["stop_loss"])

        expected_val = CalibrationService.calculate_expected_value(
            calibrated_prob,
            reward_amt,
            risk_amt,
            entry_price=price
        )

        # 7. REGIME ANALYSIS
        regime_obj = await container.ios_repo.get_latest_regime()
        regime_label = regime_obj.regime if regime_obj else "SIDEWAYS"
        regime_prob = regime_obj.sentiment_score if regime_obj else 0.5

        # 8. PRODUCTION RISK GATES
        rejection_reason = None

        # A. Drawdown Gate (Max 15%)
        if current_dd is None:
            from production.shadow.shadow_service import ShadowService
            try:
                current_dd = ShadowService.calculate_current_drawdown()
            except:
                current_dd = 0.0

        if current_dd > 15.0:
            rejection_reason = "CRITICAL_DRAWDOWN_LIMIT"

        # B. Data Freshness Gate (Max 24h)
        last_feature_date = features_list[-1].date
        if (datetime.datetime.utcnow() - last_feature_date).total_seconds() > 86400:
            rejection_reason = "STALE_MARKET_DATA"

        # C. Liquidity Gate (Min 10M Avg Volume)
        if stock.avg_volume and stock.avg_volume < 10_000_000:
            rejection_reason = "INSUFFICIENT_LIQUIDITY"

        # D. Trend Alignment Filter
        if not rejection_reason:
            ema200 = last_features.get("ema_200", price)
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
            print(f"   [NO_TRADE] {symbol} rejected: {rejection_reason}")
            return None

        # 9. DATA QUALITY SCORE
        last_feature_date = features_list[-1].date
        staleness = (datetime.datetime.utcnow() - last_feature_date).total_seconds() / 3600.0 # hours

        recent_prices = await container.repository.get_recent_prices(symbol, limit=20)
        coverage_score = min(1.0, len(recent_prices) / 20.0)
        freshness_score = max(0.0, 1.0 - (staleness / 24.0))
        data_quality = (freshness_score * 0.7) + (coverage_score * 0.3)

        # 10. Signal Eligibility Logic (Part 2)
        eligibility = "ELIGIBLE"
        if staleness > 24:
            eligibility = "STALE_DATA"
        elif coverage_score < 0.5:
            eligibility = "DATA_BLOCKED"

        # 11. Construct Canonical Signal
        sig_id = f"sig_{symbol}_{datetime.datetime.utcnow().strftime('%Y%m%d%H%M')}"
        now = datetime.datetime.utcnow()

        # Diagnostic Context (Phase 6 Robustness)
        ema200 = last_features.get("ema_200", price)
        sma20 = last_features.get("sma_20", price)
        diag_provenance = {
            "feature_version": "v1.0.0",
            "engine_version": "P0.QUANT.1",
            "calibration": "Platt-Scaled",
            "market_regime_at_entry": regime_label,
            "index_trend": regime_label,
            "sector_trend": "N/A", # Sector-level trend requires additional scan
            "relative_strength": last_features.get("rs_rating", 0.0),
            "volatility_regime": "HIGH" if regime_label == "HIGH_VOLATILITY" else "NORMAL",
            "volume_regime": "NORMAL", # Placeholder for volume outlier detection
            "EMA200_state": "ABOVE" if price > ema200 else "BELOW",
            "momentum_state": "UP" if price > sma20 else "DOWN",
            "predicted_probability": float(calibrated_prob),
            "predicted_EV": float(expected_val),
            "predicted_RR": float(risk_params["risk_reward"])
        }

        # 11.5 Persist Prediction (Workstream 6)
        from backend.domain.models.data_platform import Prediction
        pred_id = str(uuid.uuid4())
        prediction_obj = Prediction(
            id=pred_id,
            symbol=symbol,
            timestamp=now,
            model_version=ml_res.get("model_version", "TradeMind Core v2.2"),
            feature_version="v1.0.0",
            prediction="UP" if direction == "LONG" else "DOWN",
            probability=float(calibrated_prob),
            expected_value=float(expected_val),
            direction=direction,
            confidence=float(calibrated_prob),
            regime=regime_label,
            metadata=diag_provenance
        )
        await container.data_platform_repo.save_prediction(prediction_obj)

        # 11.6 AI Intelligence Synthesis (Workstream 10)
        # Fetching snapshots of other contexts
        sector_ranks = container.sector_rotation_service.get_latest_sector_rankings()
        stock_sector = next((s for s in sector_ranks if s['sector'] == stock.sector), {})
        inst_bias = container.institutional_intelligence_service.get_institutional_bias()

        container.intelligence_synthesis_service.synthesize_signal_intelligence(
            symbol=symbol,
            prediction_id=pred_id,
            market_regime=regime_label,
            sector_metrics=stock_sector,
            stock_profile=diag_provenance,
            inst_bias=inst_bias
        )

        # Part 4: Look-ahead Protection
        data_ts = features_list[-1].date
        if data_ts > now:
            print(f"   [FATAL] Look-ahead violation detected for {symbol}: {data_ts} > {now}")
            return None

        # Part 4/15/34: Evaluation Mode & Environment Guard
        from backend.core.config import settings
        eval_mode = "LIVE_SHADOW" if settings.ENVIRONMENT in ["production", "shadow"] else "TEST"

        # Hard rejection of TEST signals in production environment
        if settings.ENVIRONMENT == "production" and eval_mode == "TEST":
            print(f"   [GUARD] Rejected TEST signal generation for {symbol} in PRODUCTION.")
            return None

        return LiveSignal(
            id=sig_id,
            symbol=symbol,
            timestamp=now, # Canonical created_at
            rating="BUY" if direction == "LONG" else "SELL",
            direction=direction,
            conviction=float(calibrated_prob * 100),

            # P0 Quant Fields
            raw_probability=float(raw_prob),
            calibrated_probability=float(calibrated_prob),
            expected_value=float(expected_val),
            regime=regime_label,
            regime_probability=float(regime_prob),
            risk_reward=float(risk_params["risk_reward"]),
            risk_per_unit=float(abs(risk_amt)),
            reward_per_unit=float(abs(reward_amt)),
            data_quality_score=float(data_quality),
            signal_eligibility=eligibility,
            evaluation_mode=eval_mode,

            # Step 3 Metadata
            universe_version="NIFTY_200_AUG2026",
            strategy_version="v2.2",
            data_timestamp=data_ts,
            market_timestamp=now, # Snapshot time

            # Step 4 Scaled Dimensions (Part 21)
            quantity=1, # Default unit for shadow observation
            capital_allocation=100000.0,
            risk_amount=3000.0, # 3% risk on 100k
            outcome_verified=False,
            prediction_id=pred_id,

            entry_price=stock.last_price,
            target_price=risk_params["target"],
            stop_loss_price=risk_params["stop_loss"],
            timeframe=timeframe,
            status="WAITING_FOR_ENTRY",
            asset_class=asset_class,
            underlying_symbol=symbol if asset_class != "EQUITY" else None,
            model_version=ml_res.get("model_version", "TradeMind Core v2.2"),
            provenance=diag_provenance,
            events=[SignalEvent(type="GENERATED", message="Passed forensic P0 risk/edge audit.")]
        )
