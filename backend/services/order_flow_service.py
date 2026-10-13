"""
================================================================================
TradeMindAI: Institutional Order Flow & Cumulative Volume Delta (CVD) Service
================================================================================
Calculates order flow imbalance and cumulative volume delta from price and volume action.
"""

import pandas as pd
from typing import Dict, Any

class OrderFlowService:
    @staticmethod
    def evaluate_order_flow(df: pd.DataFrame) -> Dict[str, Any]:
        """
        Computes Cumulative Volume Delta (CVD) and Order Flow Imbalance (OFI).
        """
        if df.empty or 'close' not in df.columns or 'volume' not in df.columns:
            return {"cvd_score": 0.0, "ofi": 0.0, "institutional_accumulation": False}

        close = df['close']
        volume = df['volume']
        high = df['high'] if 'high' in df.columns else close
        low = df['low'] if 'low' in df.columns else close

        # Intra-candle buying pressure fraction (Close - Low) / (High - Low)
        hl_range = (high - low).replace(0, 0.01)
        buying_pressure = (close - low) / hl_range
        cvd = (volume * (2.0 * buying_pressure - 1.0)).sum()

        # Order Flow Imbalance over last 5 bars
        recent_vol = volume.tail(5).mean()
        avg_vol = volume.mean() if len(volume) > 0 else 1.0
        ofi = float((recent_vol / avg_vol) if avg_vol > 0 else 1.0)

        accumulation = bool(cvd > 0 and ofi >= 1.15)

        return {
            "cvd_score": round(float(cvd), 2),
            "ofi": round(ofi, 2),
            "institutional_accumulation": accumulation
        }
