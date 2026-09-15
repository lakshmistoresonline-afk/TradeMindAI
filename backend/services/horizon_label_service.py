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
    def apply_labels_to_dataset(cls, df: pd.DataFrame, horizon: str = "SWING") -> pd.DataFrame:
        """
        Applies labels to the entire dataframe for a specific horizon.
        """
        labels = []
        for i in range(len(df)):
            label = cls.calculate_label(df, i, horizon)
            labels.append(label)

        df[f"target_{horizon.lower()}"] = labels
        return df
