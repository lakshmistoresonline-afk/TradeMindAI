from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np

class HorizonLabelService:
    """
    Phase 5: Horizon-Specific Labeling Service.
    Generates target labels for ML training across different horizons.
    """

    HORIZON_CONFIG = {
        "SHORT": {
            "days": 7,
            "target_pct": 3.0,
            "stop_pct": 1.5,
            "timeout_status": "TIMEOUT"
        },
        "SWING": {
            "days": 30,
            "target_pct": 10.0,
            "stop_pct": 5.0,
            "timeout_status": "TIMEOUT"
        },
        "LONG": {
            "days": 180,
            "target_pct": 25.0,
            "stop_pct": 10.0,
            "timeout_status": "TIMEOUT"
        }
    }

    @classmethod
    def calculate_label(
        cls,
        df: pd.DataFrame,
        start_index: int,
        horizon: str = "SWING"
    ) -> Optional[int]:
        """
        Calculates a binary label (1=Success, 0=Failure) for a given row and horizon.
        Success = Target hit before Stop or Timeout.
        """
        if horizon not in cls.HORIZON_CONFIG:
            horizon = "SWING"

        config = cls.HORIZON_CONFIG[horizon]
        entry_price = df.iloc[start_index]["Close"]
        target_price = entry_price * (1 + config["target_pct"] / 100.0)
        stop_price = entry_price * (1 - config["stop_pct"] / 100.0)

        # Determine max bars to look ahead (heuristic: 1 day = 1 bar for daily data)
        # In production, we'd use actual timestamps.
        max_bars = config["days"]

        # Look ahead
        future_window = df.iloc[start_index + 1 : start_index + 1 + max_bars]

        if future_window.empty:
            return None

        for _, row in future_window.iterrows():
            high = row["High"]
            low = row["Low"]

            # Priority: Stop Loss hit first in same bar (Conservative)
            if low <= stop_price:
                return 0
            if high >= target_price:
                return 1

        # Timeout reached without hitting target or stop
        return 0

    @classmethod
    def calculate_triple_barrier_label(
        cls,
        df: pd.DataFrame,
        start_index: int,
        horizon: str = "SWING",
        pt_multiplier: float = 2.0,
        sl_multiplier: float = 1.0
    ) -> Optional[int]:
        """
        Marcos López de Prado Triple Barrier Labeling Method:
        - Upper Barrier: Profit Target = Entry + (pt_multiplier * ATR)
        - Lower Barrier: Stop Loss = Entry - (sl_multiplier * ATR)
        - Vertical Barrier: Time Expiration (max_bars)
        Returns:
            1 if Upper Barrier (Take Profit) touched before Lower Barrier or Expiration
            0 otherwise (Stop Loss touched or Time Expiration reached)
        """
        if start_index >= len(df) - 1:
            return None

        entry_price = df.iloc[start_index]["Close"]
        atr = df.iloc[start_index].get("ATR")
        if not atr or atr <= 0:
            atr = entry_price * 0.02

        config = cls.HORIZON_CONFIG.get(horizon, cls.HORIZON_CONFIG["SWING"])
        max_bars = config["days"]

        upper_barrier = entry_price + (pt_multiplier * atr)
        lower_barrier = entry_price - (sl_multiplier * atr)

        future_window = df.iloc[start_index + 1 : start_index + 1 + max_bars]
        if future_window.empty:
            return None

        for _, row in future_window.iterrows():
            high = row["High"]
            low = row["Low"]

            # Lower barrier (Stop Loss) priority
            if low <= lower_barrier:
                return 0
            if high >= upper_barrier:
                return 1

        # Vertical barrier (Time Expiration) reached
        return 0

    @classmethod
    def apply_labels_to_dataset(cls, df: pd.DataFrame, horizon: str = "SWING", use_triple_barrier: bool = True) -> pd.DataFrame:
        """
        Applies labels to the entire dataframe for a specific horizon.
        Supports Triple Barrier Method.
        """
        labels = []
        for i in range(len(df)):
            if use_triple_barrier:
                label = cls.calculate_triple_barrier_label(df, i, horizon)
            else:
                label = cls.calculate_label(df, i, horizon)
            labels.append(label)

        df[f"target_{horizon.lower()}"] = labels
        return df
