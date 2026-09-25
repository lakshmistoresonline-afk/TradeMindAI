from typing import Dict, Any, Optional, Tuple
import numpy as np
from backend.core.config import settings

class RiskEngine:
    @staticmethod
    def calculate_trade_parameters(
        symbol: str,
        price: float,
        direction: str,
        atr: float,
        horizon: str = "SWING",
        regime: str = "BULL",
        risk_per_trade: float = 0.02, # 2% of capital
        capital: float = 1000000.0    # 10 Lakhs baseline
    ) -> Dict[str, Any]:
        """
        Calculates Stop Loss, 3 Targets (T1, T2, T3), and Position Sizing using Regime-Aware Adaptive ATR
        and Portfolio Risk rules.
        - Target 1 (T1): Conservative 1.5x ATR (1:1.5 Risk/Reward)
        - Target 2 (T2): Main Structural 2.8x ATR (1:2.5 Risk/Reward)
        - Target 3 (T3): Extended Runner 4.2x ATR (1:4.0 Risk/Reward)
        """
        if price <= 0 or atr <= 0:
            return {}

        # 1. Horizon & Regime Specific Multipliers
        horizon_configs = {
            "SHORT": {"stop_mult": 1.5, "rr": 2.0},
            "SWING": {"stop_mult": 2.0, "rr": 2.5},
            "LONG": {"stop_mult": 3.0, "rr": 3.0}
        }
        config = horizon_configs.get(horizon, horizon_configs["SWING"])

        regime_adjustments = {
            "BULL": {"stop_factor": 1.0, "target_factor": 1.0},
            "BEAR": {"stop_factor": 1.0, "target_factor": 1.0},
            "SIDEWAYS": {"stop_factor": 0.9, "target_factor": 0.8},        # Tighter stop & target for chop
            "HIGH_VOLATILITY": {"stop_factor": 1.4, "target_factor": 1.3}, # Wider stop buffer to prevent noise stop
            "LOW_VOLATILITY": {"stop_factor": 0.85, "target_factor": 0.9},
            "TRANSITION": {"stop_factor": 1.1, "target_factor": 1.1}
        }
        adj = regime_adjustments.get(regime.upper() if regime else "BULL", {"stop_factor": 1.0, "target_factor": 1.0})

        stop_mult = config["stop_mult"] * adj["stop_factor"]
        rr_ratio = round(config["rr"] * (adj["target_factor"] / adj["stop_factor"]), 2)

        risk_amt = atr * stop_mult

        if direction == "LONG":
            stop_loss = price - risk_amt
            target_1 = price + (risk_amt * 1.5)
            target_2 = price + (risk_amt * 2.8)
            target_3 = price + (risk_amt * 4.2)
        else:
            stop_loss = price + risk_amt
            target_1 = price - (risk_amt * 1.5)
            target_2 = price - (risk_amt * 2.8)
            target_3 = price - (risk_amt * 4.2)

        # 2. Position Sizing (Fixed Fractional)
        total_risk_cap = capital * risk_per_trade
        shares = total_risk_cap / risk_amt if risk_amt > 0 else 0

        # 3. Liquidity/Volatility Constraint
        max_notional = capital * 0.10
        shares_limit = max_notional / price
        final_shares = int(min(shares, shares_limit))

        return {
            "entry": float(price),
            "stop_loss": round(float(stop_loss), 2),
            "target": round(float(target_2), 2),     # Main Target 2 fallback
            "target_1": round(float(target_1), 2),   # T1 Conservative (1:1.5)
            "target_2": round(float(target_2), 2),   # T2 Main Structural (1:2.5)
            "target_3": round(float(target_3), 2),   # T3 Extended Runner (1:4.0)
            "risk_reward": rr_ratio,
            "shares": final_shares,
            "notional_value": round(final_shares * price, 2),
            "risk_amount": round(final_shares * (abs(price - stop_loss)), 2),
            "risk_pct": round((abs(price - stop_loss) / price) * 100, 2),
            "regime_applied": regime
        }

    @staticmethod
    def evaluate_risk_quality(params: Dict[str, Any], regime: str) -> str:
        """
        Rejects or grades signals based on regime-risk alignment.
        """
        risk_pct = params.get("risk_pct", 0)

        if risk_pct > 15: return "REJECT (Excessive Volatility)"
        if risk_pct < 0.5: return "REJECT (Stale Data/Flat)"

        if regime == "VOLATILE" and risk_pct > 8:
            return "C (High Risk Context)"

        if regime == "BULLISH" and params.get("direction") == "LONG":
            return "A+ (Regime Aligned)"

        return "B (Standard)"
