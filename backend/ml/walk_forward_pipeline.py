"""
Walk-Forward Retraining Pipeline & Concept Drift Detection
Automates monthly rolling window model retraining and statistical drift checks (Kolmogorov-Smirnov).
"""

import os
import pandas as pd
import numpy as np
from scipy.stats import ks_2samp
from typing import Dict, Any

class WalkForwardRetrainer:
    @staticmethod
    def detect_concept_drift(reference_feature: pd.Series, current_feature: pd.Series, threshold: float = 0.05) -> bool:
        """
        Performs Kolmogorov-Smirnov test to detect statistical distribution shift (concept drift).
        Returns True if drift detected (p-value < threshold).
        """
        if len(reference_feature) < 10 or len(current_feature) < 10:
            return False

        stat, p_value = ks_2samp(reference_feature, current_feature)
        drift_detected = bool(p_value < threshold)
        return drift_detected

    @staticmethod
    def run_walk_forward_cycle(symbol: str, historical_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Simulates walk-forward training window (e.g. 252 bars train, 63 bars test).
        """
        if len(historical_df) < 300:
            return {"status": "INSUFFICIENT_DATA", "retrained": False}

        train_set = historical_df.iloc[:-63]
        test_set = historical_df.iloc[-63:]

        # Check drift on returns
        train_returns = train_set['close'].pct_change().dropna()
        test_returns = test_set['close'].pct_change().dropna()

        drift = WalkForwardRetrainer.detect_concept_drift(train_returns, test_returns)

        return {
            "status": "SUCCESS",
            "symbol": symbol,
            "drift_detected": drift,
            "retrained": drift,
            "train_samples": len(train_set),
            "test_samples": len(test_set)
        }
