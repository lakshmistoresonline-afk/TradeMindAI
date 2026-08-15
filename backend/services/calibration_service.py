import numpy as np
from typing import List, Dict, Any

class CalibrationService:
    @staticmethod
    def calibrate_probability(raw_prob: float, asset_class: str) -> float:
        """
        Calibrates raw ML probabilities using segment-specific historical offsets.
        Baseline: Platt-like scaling for production safety.
        """
        # Segment-specific calibration factors (derived from forensic audit)
        offsets = {
            "EQUITY": 0.05,    # Overconfident in breakouts
            "FUTURES": -0.02,   # Underconfident in trending markets
            "OPTIONS": 0.10     # Significant decay/volatility skew
        }

        factor = offsets.get(asset_class, 0.0)

        # Sigmoid-based squash
        calibrated = 1 / (1 + np.exp(-(raw_prob - 0.5 - factor) * 10))

        return round(float(calibrated), 3)

    @staticmethod
    def calculate_expected_value(prob: float, target_pct: float, stop_pct: float) -> float:
        """
        EV = (P_win * Win_Amt) - (P_loss * Loss_Amt)
        """
        if target_pct <= 0 or stop_pct >= 0:
            # Handle short or invalid inputs
            target_pct = abs(target_pct)
            stop_pct = abs(stop_pct)

        ev = (prob * target_pct) - ((1 - prob) * stop_pct)
        return round(float(ev), 2)
