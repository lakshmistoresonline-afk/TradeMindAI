import numpy as np
from typing import List, Dict, Any

class CalibrationService:
    @staticmethod
    def calibrate_probability(raw_prob: float, asset_class: str) -> float:
        """
        Calibrates raw ML probabilities using Platt Scaling (Sigmoid transformation).
        Baseline: Statistical mapping to real-world win frequencies.
        """
        if raw_prob is None: return 0.5

        # Segment-specific calibration parameters (A and B for Sigmoid)
        # These would be optimized locally during Step 3 Training.
        params = {
            "EQUITY": {"a": -5.0, "b": 0.5},
            "FUTURES": {"a": -4.2, "b": 0.3},
            "OPTIONS": {"a": -6.5, "b": 1.2}
        }

        p = params.get(asset_class, {"a": -5.0, "b": 0.5})

        # Platt Scaling: P(y=1|x) = 1 / (1 + exp(A*f(x) + B))
        # where f(x) is the raw logit or probability-like output
        calibrated = 1 / (1 + np.exp(p["a"] * (raw_prob - 0.5) + p["b"]))

        return round(float(calibrated), 3)

    @staticmethod
    def calculate_expected_value(prob: float, reward_amt: float, risk_amt: float) -> float:
        """
        Calculates real-world Expected Value (EV) per unit.
        EV = (P_win * Reward) - (P_loss * Risk) - Transaction Costs
        """
        if prob is None or prob <= 0: return -1.0

        # Estimate slippage + brokerage (institutional baseline: 0.1% per leg)
        slippage = (reward_amt + risk_amt) * 0.001

        ev = (prob * reward_amt) - ((1 - prob) * risk_amt) - slippage
        return round(float(ev), 2)
