import numpy as np
from typing import List, Dict, Any, Optional

class CalibrationService:
    # Institutional cost assumptions (configurable via settings in future)
    TRANSACTION_COST_PCT = 0.0005 # 0.05% per leg (brokerage + STT + SEBI)
    SLIPPAGE_PCT = 0.0005 # 0.05% expected slippage

    @staticmethod
    def calibrate_probability(raw_prob: float, asset_class: str, params: Optional[Dict[str, float]] = None) -> float:
        """
        Calibrates raw ML probabilities using Platt Scaling (Sigmoid transformation).
        Uses provided params or segment-specific institutional baselines.
        """
        if raw_prob is None: return 0.5

        if not params:
            # Segment-specific institutional baseline calibration parameters
            params_map = {
                "EQUITY": {"a": -5.0, "b": 0.5},
                "FUTURES": {"a": -4.2, "b": 0.3},
                "OPTIONS": {"a": -6.5, "b": 1.2}
            }
            p = params_map.get(asset_class, {"a": -5.0, "b": 0.5})
        else:
            p = params

        # Platt Scaling: P(y=1|x) = 1 / (1 + exp(A*f(x) + B))
        calibrated = 1 / (1 + np.exp(p["a"] * (raw_prob - 0.5) + p["b"]))

        return round(float(calibrated), 3)

    @staticmethod
    def calculate_expected_value(prob: float, reward_amt: float, risk_amt: float, entry_price: float = 0.0) -> float:
        """
        Calculates real-world Expected Value (EV) per unit.
        EV = (P_win * Reward) - (P_loss * Risk) - Transaction Costs - Slippage
        """
        if prob is None or prob <= 0: return -1.0

        reward_amt = abs(reward_amt)
        risk_amt = abs(risk_amt)

        # Friction calculation
        # If entry_price is provided, use total transaction value friction (standard institutional)
        # Otherwise fall back to movement-based friction (simplified)
        if entry_price > 0:
            # Entry + Exit friction
            avg_exit = entry_price + (reward_amt - risk_amt) / 2 # simplified mid-point
            total_value = entry_price + avg_exit
            total_friction = total_value * (CalibrationService.TRANSACTION_COST_PCT + CalibrationService.SLIPPAGE_PCT)
        else:
            total_friction = (reward_amt + risk_amt) * (CalibrationService.TRANSACTION_COST_PCT + CalibrationService.SLIPPAGE_PCT)

        ev = (prob * reward_amt) - ((1 - prob) * risk_amt) - total_friction
        return round(float(ev), 2)

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
