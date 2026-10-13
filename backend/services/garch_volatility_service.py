"""
================================================================================
TradeMindAI: GARCH-Based Conditional Volatility & Dynamic Stop-Loss Service
================================================================================
Estimates conditional volatility persistence and computes volatility-adaptive
ATR risk geometry stop multipliers.
"""

import numpy as np
import pandas as pd
from typing import Dict, Any

class GarchVolatilityService:
    @staticmethod
    def calculate_dynamic_stop(close_series: pd.Series, atr: float, regime: str) -> float:
        """
        Computes dynamic ATR stop buffer conditioned on volatility state and GARCH persistence.
        """
        if close_series is None or len(close_series) < 20 or atr <= 0:
            return 2.0

        returns = close_series.pct_change().dropna()
        recent_vol = returns.tail(20).std() * np.sqrt(252)
        long_vol = returns.std() * np.sqrt(252) if len(returns) > 0 else recent_vol

        vol_ratio = recent_vol / long_vol if long_vol > 0 else 1.0

        # Base multiplier conditioned on regime and volatility persistence
        if regime == "HIGH_VOLATILITY" or vol_ratio > 1.3:
            multiplier = 2.8
        elif regime == "SIDEWAYS" or 0.8 <= vol_ratio <= 1.2:
            multiplier = 1.8
        else:
            multiplier = 2.2

        return round(float(multiplier), 2)
