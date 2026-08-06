from datetime import datetime
from backend.domain.models.ios import MarketRegime

class MarketRegimeEngine:
    @staticmethod
    def detect_regime(nifty_df: Any, vix_value: float) -> MarketRegime:
        """
        Institutional Market Regime Detection logic.
        Uses Nifty 50 returns and India VIX.
        """
        if nifty_df is None or len(nifty_df) < 50: # Need at least 50 days for rolling mean
            return MarketRegime(
                date=datetime.utcnow(), regime="SIDEWAYS", risk_mode="RISK_OFF",
                sentiment_score=0.5, volatility_index=vix_value,
                description="Insufficient benchmark data to detect regime. Defaulting to SIDEWAYS."
            )

        import pandas as pd
        import numpy as np

        returns = nifty_df["Close"].pct_change().tail(20) # Last 20 days
        avg_return = returns.mean()
        volatility = returns.std()

        # 1. Regime Logic
        regime = "SIDEWAYS"
        if avg_return > 0.001 and nifty_df["Close"].iloc[-1] > nifty_df["Close"].rolling(50).mean().iloc[-1]:
            regime = "BULL"
        elif avg_return < -0.001 and nifty_df["Close"].iloc[-1] < nifty_df["Close"].rolling(50).mean().iloc[-1]:
            regime = "BEAR"

        if vix_value > 20:
            regime = "VOLATILE " + regime

        # 2. Risk Mode
        risk_mode = "RISK_ON" if vix_value < 16 and avg_return > 0 else "RISK_OFF"

        return MarketRegime(
            date=datetime.utcnow(),
            regime=regime,
            risk_mode=risk_mode,
            sentiment_score=float(0.5 + avg_return * 10), # Simplified sentiment mapping
            volatility_index=vix_value,
            description=f"Market is in a {regime} phase. {risk_mode} behavior observed."
        )
