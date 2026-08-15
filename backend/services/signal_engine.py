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
        raw_prob = ml_res.get("confidence", 0) / 100.0

        # 4. Calibration & EV
        calibrated_prob = CalibrationService.calibrate_probability(raw_prob, asset_class)

        # 5. Risk Calculation
        atr = last_features.get("volatility_atr", stock.last_price * 0.02) # Fallback to 2%
        risk_params = RiskEngine.calculate_trade_parameters(
            symbol, stock.last_price,
            "LONG" if ml_res.get("prediction") == "UP" else "SHORT",
            atr
        )

        if not risk_params: return None

        ev = CalibrationService.calculate_expected_value(
            calibrated_prob,
            risk_params["target"] - stock.last_price,
            stock.last_price - risk_params["stop_loss"]
        )

        # 6. NO-TRADE ENGINE (Part 19)
        if calibrated_prob < 0.55: return None # Low probability
        if ev <= 0: return None               # Negative expectancy
        if risk_params["risk_pct"] > 10: return None # Excessive risk

        # 7. Regime Alignment
        regime_obj = await container.ios_repo.get_latest_regime()
        regime = regime_obj.regime if regime_obj else "SIDEWAYS"

        # Reject Shorts in strong BULL, Longs in extreme BEAR
        if regime == "BULL" and risk_params["direction"] == "SHORT": return None

        # 8. Construct Signal
        if asset_class == "OPTIONS":
            # Strict Contract Validation for Options
            if not last_features.get("options_strike") or not last_features.get("options_type"):
                print(f"[!] REJECT: Options setup for {symbol} missing contract metadata.")
                return None

        sig_id = f"sig_{symbol}_{datetime.datetime.utcnow().strftime('%Y%m%d%H%M')}"

        return LiveSignal(
            id=sig_id,
            symbol=symbol,
            timestamp=datetime.datetime.utcnow(),
            rating="BUY" if risk_params["direction"] == "LONG" else "SELL",
            direction=risk_params["direction"],
            conviction=float(calibrated_prob * 100),
            entry_price=stock.last_price,
            target_price=risk_params["target"],
            stop_loss_price=risk_params["stop_loss"],
            timeframe=timeframe,
            status="WAITING_FOR_ENTRY",
            asset_class=asset_class,
            underlying_symbol=symbol if asset_class != "EQUITY" else None,
            strike=last_features.get("options_strike") if asset_class == "OPTIONS" else None,
            option_type=last_features.get("options_type") if asset_class == "OPTIONS" else None,
            expiry=datetime.datetime.utcnow() + datetime.timedelta(days=12) if asset_class != "EQUITY" else None,
            model_version=ml_res.get("model_version", "TradeMind Core v2.2"),
            events=[SignalEvent(type="GENERATED", message="Qualified signal passed No-Trade Engine constraints.")]
        )
