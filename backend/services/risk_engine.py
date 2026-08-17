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
        risk_per_trade: float = 0.02, # 2% of capital
        capital: float = 1000000.0    # 10 Lakhs baseline
    ) -> Dict[str, Any]:
        """
        Calculates Stop Loss, Target, and Position Sizing using ATR and Portfolio Risk rules.
        """
        if price <= 0 or atr <= 0:
            return {}

        # 1. Stop Loss (2.0x ATR multiplier for Swing)
        stop_mult = 2.0
        risk_amt = atr * stop_mult
        rr_ratio = settings.DEFAULT_RISK_REWARD

        if direction == "LONG":
            stop_loss = price - risk_amt
            target = price + (risk_amt * rr_ratio)
        else:
            stop_loss = price + risk_amt
            target = price - (risk_amt * rr_ratio)

        # 2. Position Sizing (Fixed Fractional)
        # amt_to_risk = 1,000,000 * 0.02 = 20,000
        total_risk_cap = capital * risk_per_trade

        # shares = risk_cap / risk_per_share
        shares = total_risk_cap / risk_amt if risk_amt > 0 else 0

        # 3. Liquidity/Volatility Constraint
        # Limit exposure to 10% of total capital per trade
        max_notional = capital * 0.10
        shares_limit = max_notional / price

        final_shares = int(min(shares, shares_limit))

        return {
            "entry": float(price),
            "stop_loss": round(float(stop_loss), 2),
            "target": round(float(target), 2),
            "risk_reward": rr_ratio,
            "shares": final_shares,
            "notional_value": round(final_shares * price, 2),
            "risk_amount": round(final_shares * (abs(price - stop_loss)), 2),
            "risk_pct": round((abs(price - stop_loss) / price) * 100, 2)
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
