from typing import List, Dict, Any, Optional
import datetime
import uuid
from backend.domain.models.ios import LiveSignal, SignalEvent
from backend.services.regime_engine import MarketRegimeEngine
from backend.services.risk_engine import RiskEngine
from backend.services.calibration_service import CalibrationService
from backend.core.container import container

class SignalEngine:
    @staticmethod
    async def generate_signal(symbol: str, asset_class: str, timeframe: str) -> Optional[LiveSignal]:
        """
        Master Signal Generation Node.
        Implements No-Trade Engine and Probability Calibration.
        """
        # 1. Fetch Fresh Data
        stock = await container.repository.get_stock_by_symbol(symbol)
        if not stock: return None

        # 2. Extract Features (Time-Safe)
        features_list = await container.data_platform_repo.get_features_by_range(
            symbol,
            datetime.datetime.utcnow() - datetime.timedelta(days=7),
            datetime.datetime.utcnow()
        )
        if not features_list: return None
        last_features = features_list[-1].features

        # 3. Model Inference (Champion Model)
        ml_res = await container.ml_service.predict_with_champion(symbol, last_features)

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
        atr = last_features.get("volatility_atr", price * 0.02)
        risk_params = RiskEngine.calculate_trade_parameters(
            symbol, price,
            direction,
            atr
        )

        if not risk_params: return None

        # 6. EXPECTED VALUE
        # EV = P(win) * Reward - P(loss) * Risk
        # Ensure absolute values for direction-neutral math
        reward_amt = abs(risk_params["target"] - price)
        risk_amt = abs(price - risk_params["stop_loss"])

        expected_val = CalibrationService.calculate_expected_value(
            calibrated_prob,
            reward_amt,
            risk_amt
        )

        # 7. REGIME ANALYSIS
        regime_obj = await container.ios_repo.get_latest_regime()
        regime_label = regime_obj.regime if regime_obj else "SIDEWAYS"
        regime_prob = regime_obj.sentiment_score if regime_obj else 0.5

        # 8. NO-TRADE ENGINE
        rejection_reason = None
        # Valid Geometry Check
        if reward_amt <= 0 or risk_amt <= 0: rejection_reason = "INVALID_GEOMETRY"
        elif calibrated_prob < 0.52: rejection_reason = "WEAK_EDGE"
        elif expected_val <= 0: rejection_reason = "NEGATIVE_EXPECTANCY"
        elif risk_params["risk_pct"] > 12: rejection_reason = "EXCESSIVE_VOLATILITY"
        elif regime_label == "HIGH_VOLATILITY" and calibrated_prob < 0.65: rejection_reason = "REGIME_CONFLICT"

        if rejection_reason:
            print(f"   [NO_TRADE] {symbol} rejected: {rejection_reason}")
            return None

        # 9. Construct Canonical Signal
        sig_id = f"sig_{symbol}_{datetime.datetime.utcnow().strftime('%Y%m%d%H%M')}"

        return LiveSignal(
            id=sig_id,
            symbol=symbol,
            timestamp=datetime.datetime.utcnow(),
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
            data_quality_score=1.0, # TODO: Implement real data quality check

            entry_price=stock.last_price,
            target_price=risk_params["target"],
            stop_loss_price=risk_params["stop_loss"],
            timeframe=timeframe,
            status="WAITING_FOR_ENTRY",
            asset_class=asset_class,
            underlying_symbol=symbol if asset_class != "EQUITY" else None,
            model_version=ml_res.get("model_version", "TradeMind Core v2.2"),
            provenance={
                "feature_version": "v1.0.0",
                "engine_version": "P0.QUANT.1",
                "calibration": "Platt-Scaled"
            },
            events=[SignalEvent(type="GENERATED", message="Passed forensic P0 risk/edge audit.")]
        )
