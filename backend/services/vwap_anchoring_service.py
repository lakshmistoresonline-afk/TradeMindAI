"""
================================================================================
TradeMindAI: Multi-Timeframe Microstructure VWAP Anchoring Service
================================================================================
Evaluates session VWAP distance and precision entry fill quality.
"""

import pandas as pd
from typing import Dict, Any

class VWAPAnchoringService:
    @staticmethod
    def evaluate_vwap_alignment(df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculates session VWAP and price deviation percentage.
        """
        if df.empty or 'close' not in df.columns or 'volume' not in df.columns:
            return {"vwap": 0.0, "vwap_deviation_pct": 0.0, "vwap_aligned": True}

        typical_price = (df['high'] + df['low'] + df['close']) / 3.0 if ('high' in df.columns and 'low' in df.columns) else df['close']
        vwap = (typical_price * df['volume']).cumsum() / df['volume'].cumsum().replace(0, 1)
        latest_vwap = float(vwap.iloc[-1])
        latest_close = float(df['close'].iloc[-1])

        deviation_pct = abs(latest_close - latest_vwap) / latest_vwap * 100.0 if latest_vwap > 0 else 0.0
        aligned = bool(deviation_pct <= 0.75) # Within 0.75% of anchored VWAP

        return {
            "vwap": round(latest_vwap, 2),
            "vwap_deviation_pct": round(deviation_pct, 2),
            "vwap_aligned": aligned
        }
