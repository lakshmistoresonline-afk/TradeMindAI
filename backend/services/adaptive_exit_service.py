"""
================================================================================
TradeMindAI: Reinforcement & Momentum Decay Adaptive Exit Manager
================================================================================
Dynamically adjusts profit targets and trailing stops based on real-time
momentum exhaustion and order flow divergence.
"""

import pandas as pd
from typing import Dict, Any

class AdaptiveExitService:
    @staticmethod
    def evaluate_adaptive_exits(df: pd.DataFrame, current_target: float, current_stop: float) -> Dict[str, Any]:
        """
        Dynamically adjusts exit geometry during momentum acceleration or divergence.
        """
        if df.empty or 'close' not in df.columns:
            return {"adjusted_target": current_target, "adjusted_stop": current_stop, "momentum_state": "NORMAL"}

        close = df['close']
        recent_return = (close.iloc[-1] - close.iloc[-5]) / close.iloc[-5] if len(close) >= 5 else 0.0

        # If strong momentum expansion, extend target by 15%
        if recent_return > 0.03:
            adjusted_target = current_target * 1.15
            adjusted_stop = current_stop * 1.01 # Tighten trailing stop
            state = "MOMENTUM_EXPANSION"
        elif recent_return < -0.02:
            adjusted_target = current_target * 0.90
            adjusted_stop = current_stop
            state = "MOMENTUM_DECAY"
        else:
            adjusted_target = current_target
            adjusted_stop = current_stop
            state = "NORMAL"

        return {
            "adjusted_target": round(float(adjusted_target), 2),
            "adjusted_stop": round(float(adjusted_stop), 2),
            "momentum_state": state
        }
