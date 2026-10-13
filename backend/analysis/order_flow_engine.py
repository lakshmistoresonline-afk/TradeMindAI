"""
Order Flow & Cumulative Volume Delta (CVD) Engine
Calculates Order Flow Imbalance (OFI) and CVD divergence metrics from intraday price/volume bars.
"""

import numpy as np
import pandas as pd
from typing import Dict, Any

class OrderFlowEngine:
    @staticmethod
    def calculate_cvd_and_ofi(df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculates Cumulative Volume Delta and Order Flow Imbalance.
        Expected columns: ['open', 'high', 'low', 'close', 'volume']
        """
        if df is None or len(df) < 5:
            return {"cvd": 0.0, "ofi": 0.0, "divergence": False}

        # Estimate aggressive buying vs selling using close relative to high-low range
        hl_range = df['high'] - df['low']
        hl_range = hl_range.replace(0, 0.001)

        # Buying pressure fraction (0 to 1)
        buying_pressure = (df['close'] - df['low']) / hl_range
        delta = df['volume'] * (2 * buying_pressure - 1)

        cvd = float(delta.cumsum().iloc[-1])

        # Order Flow Imbalance (OFI) based on bid/ask volume approximation
        price_diff = df['close'].diff().fillna(0)
        ofi = float((np.sign(price_diff) * df['volume']).rolling(window=5).sum().iloc[-1])

        # CVD divergence detection: price making higher high while CVD making lower high
        price_trend = df['close'].iloc[-1] > df['close'].iloc[-5]
        cvd_series = delta.cumsum()
        cvd_trend = cvd_series.iloc[-1] > cvd_series.iloc[-5]
        divergence = bool(price_trend != cvd_trend)

        return {
            "cvd": cvd,
            "ofi": ofi,
            "divergence": divergence
        }
