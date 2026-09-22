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
    def calibrate_isotonic(raw_prob: float, calibrator_model: Any = None, asset_class: str = "EQUITY") -> float:
        """
        Calibrates probability using an Isotonic Regression / Calibrated Classifier fitted model if available,
        falling back to Platt scaling.
        """
        if raw_prob is None:
            return 0.5

        if calibrator_model is not None:
            try:
                prob_arr = np.array([[raw_prob]])
                if hasattr(calibrator_model, "predict_proba"):
                    calibrated = float(calibrator_model.predict_proba(prob_arr)[0][1])
                elif hasattr(calibrator_model, "predict"):
                    calibrated = float(calibrator_model.predict(np.array([raw_prob]))[0])
                else:
                    calibrated = raw_prob
                return round(float(np.clip(calibrated, 0.0, 1.0)), 3)
            except Exception:
                pass

        return CalibrationService.calibrate_probability(raw_prob, asset_class)

    @staticmethod
    def calculate_expected_calibration_error(y_true: np.ndarray, y_prob: np.ndarray, n_bins: int = 10) -> float:
        """
        Calculates Expected Calibration Error (ECE):
        ECE = sum_{b=1}^B (|B_b| / N) * | acc(B_b) - conf(B_b) |
        """
        if len(y_true) == 0 or len(y_prob) == 0:
            return 0.0

        bins = np.linspace(0.0, 1.0, n_bins + 1)
        binids = np.digitize(y_prob, bins) - 1

        ece = 0.0
        n_samples = len(y_prob)

        for i in range(n_bins):
            bin_filter = binids == i
            bin_size = np.sum(bin_filter)

            if bin_size > 0:
                bin_acc = np.mean(y_true[bin_filter])
                bin_conf = np.mean(y_prob[bin_filter])
                ece += (bin_size / n_samples) * abs(bin_acc - bin_conf)

        return round(float(ece), 4)

    @staticmethod
    def calculate_corwin_schultz_spread(high: np.ndarray, low: np.ndarray) -> float:
        """
        Corwin-Schultz (2012) High-Low Bid-Ask Spread Estimator:
        S = 2 * (exp(alpha) - 1) / (1 + exp(alpha))
        """
        if len(high) < 2 or len(low) < 2:
            return 0.0010 # Default 0.10%

        try:
            h1, l1 = float(high[-2]), float(low[-2])
            h2, l2 = float(high[-1]), float(low[-1])

            if l1 <= 0 or l2 <= 0: return 0.0010

            gamma = (np.log(max(h1, h2) / min(l1, l2))) ** 2
            beta = (np.log(h1 / l1)) ** 2 + (np.log(h2 / l2)) ** 2

            denom = 3 - 2 * np.sqrt(2)
            alpha = (np.sqrt(2 * beta) - np.sqrt(beta)) / denom - np.sqrt(gamma / denom)

            if alpha <= 0: return 0.0005

            spread = 2 * (np.exp(alpha) - 1) / (1 + np.exp(alpha))
            return round(float(np.clip(spread, 0.0002, 0.05)), 4)
        except Exception:
            return 0.0010

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
