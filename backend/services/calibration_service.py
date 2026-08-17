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
    def get_direction_probability(prob_up: float, direction: str) -> float:
        """
        Maps probability of 'UP' to the probability of the actual trade direction.
        For LONG: P(UP)
        For SHORT: 1 - P(UP)
        """
        if prob_up is None: return 0.5

        # Clamp to [0, 1]
        prob_up = max(0.0, min(1.0, prob_up))

        if direction.upper() in ["BUY", "LONG"]:
            return prob_up
        elif direction.upper() in ["SELL", "SHORT"]:
            return 1.0 - prob_up
        return 0.5

    @staticmethod
    def calculate_expected_value(prob: float, reward_amt: float, risk_amt: float) -> float:
        """
        Calculates real-world Expected Value (EV) per unit.
        EV = (P_win * Reward) - (P_loss * Risk) - Transaction Costs
        NOTE: reward_amt and risk_amt MUST be absolute positive values.
        """
        if prob is None or prob <= 0: return -1.0

        # Absolute values to ensure math works for both LONG and SHORT
        reward_amt = abs(reward_amt)
        risk_amt = abs(risk_amt)

        # Estimate slippage + brokerage (institutional baseline: 0.1% per leg)
        slippage = (reward_amt + risk_amt) * 0.001

        ev = (prob * reward_amt) - ((1 - prob) * risk_amt) - slippage
        return round(float(ev), 2)
