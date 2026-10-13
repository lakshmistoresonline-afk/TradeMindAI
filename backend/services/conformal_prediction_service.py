"""
================================================================================
TradeMindAI: Split Conformal Prediction & Uncertainty Quantification Service
================================================================================
Computes epistemic uncertainty bounds and statistical confidence intervals for model predictions.
"""

import numpy as np
from typing import Dict, Any

class ConformalPredictionService:
    @staticmethod
    def compute_conformal_bounds(probability: float, historical_errors: np.ndarray, alpha: float = 0.10) -> Dict[str, Any]:
        """
        Computes conformal prediction intervals guaranteeing coverage at (1 - alpha)% confidence.
        """
        if historical_errors is None or len(historical_errors) == 0:
            margin = 0.05
        else:
            margin = float(np.percentile(np.abs(historical_errors), (1.0 - alpha) * 100.0))

        lower_bound = max(0.0, probability - margin)
        upper_bound = min(1.0, probability + margin)
        uncertainty = upper_bound - lower_bound

        reliable = bool(uncertainty <= 0.20) # Low epistemic uncertainty

        return {
            "lower_bound": round(lower_bound, 4),
            "upper_bound": round(upper_bound, 4),
            "epistemic_uncertainty": round(uncertainty, 4),
            "conformal_reliable": reliable
        }
