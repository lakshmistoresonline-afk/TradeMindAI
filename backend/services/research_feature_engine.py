import datetime
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from backend.analysis.technical import TechnicalAnalysis
from backend.services.feature_store import FeatureStoreService
from backend.core.container import container

class ResearchFeatureEngine:
    """
    Phases 5-6: Canonical Historical Feature Engine.
    Handles bulk feature generation and time-safe labeling for multi-horizon research.
    """

    @staticmethod
    def generate_labels(df: pd.DataFrame, horizon_days: int, target_pct: float) -> pd.Series:
        """
        Generates binary labels: 1 if target reached before stop or timeout.
        Standard rule: 1:1 risk/reward for labeling if not specified,
        but here we use target_pct and a 0.5 * target_pct stop.
        """
        labels = pd.Series(index=df.index, data=0)
        close = df['Close']

        stop_pct = target_pct * 0.5 # 1:2 Risk/Reward default for research labels

        for i in range(len(df) - horizon_days):
            entry_price = close.iloc[i]
            future_segment = close.iloc[i+1 : i+1+horizon_days]

            # LONG side only for now (Standard Equity Intelligence)
            target_price = entry_price * (1 + target_pct/100.0)
            stop_price = entry_price * (1 - stop_pct/100.0)

            # Check if target hit before stop
            reached_target = False
            for p in future_segment:
                if p >= target_price:
                    reached_target = True
                    break
                if p <= stop_price:
                    break

            if reached_target:
                labels.iloc[i] = 1

        return labels

    @staticmethod
    async def build_horizon_dataset(symbol: str, horizon: str) -> pd.DataFrame:
        """
        Builds a complete feature+label dataset for a specific horizon.
        """
        # 1. Fetch ALL available history
        df_raw = await container.historical_data_service.get_validated_history(
            symbol,
            start_date=datetime.datetime(2020, 1, 1)
        )
        if df_raw.empty or len(df_raw) < 200:
            return pd.DataFrame()

        # 2. Calculate Indicators
        df_ta = TechnicalAnalysis.calculate_indicators(df_raw)

        # 3. Generate Labels based on horizon
        params = {
            "SHORT": {"days": 3, "target": 3.0},
            "SWING": {"days": 15, "target": 10.0},
            "LONG": {"days": 60, "target": 25.0}
        }
        p = params.get(horizon, params["SWING"])
        df_ta["target"] = ResearchFeatureEngine.generate_labels(df_ta, p["days"], p["target"])

        # 4. Extract Model Features (Row-by-Row is slow, use vectorized mapping where possible)
        # For simplicity and correctness, we iterate or use a specialized vectorized feature extractor.
        # But wait, extract_institutional_features is designed for one row.

        # Let's create a vectorized version or just use the columns directly since we calculated them in TechnicalAnalysis
        feature_cols = [
            "ema_20", "sma_20", "ema_50", "ema_100", "ema_200",
            "ema_20_slope", "ema_200_slope",
            "momentum_rsi", "momentum_roc", "macd_hist", "stoch_k", "momentum_cci",
            "adx", "dmp", "dmn", "natr", "volatility_bb_width", "volatility_bb_pct",
            "hist_vol", "volume_relative", "obv", "mfi", "trend_ema_cross"
        ]

        # Clean data
        dataset = df_ta[feature_cols + ["target"]].copy()
        dataset.replace([np.inf, -np.inf], np.nan, inplace=True)
        dataset.dropna(inplace=True)

        return dataset
