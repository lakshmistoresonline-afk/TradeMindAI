"""
================================================================================
TradeMindAI: Advanced Stacking Meta-Learner (Ensemble V3.3)
================================================================================
Combines probability outputs from base estimators (GradientBoosting, ExtraTrees, RandomForest)
using a meta-learning probability calibration layer.
"""

import numpy as np
from typing import List, Dict, Any

class StackingMetaLearner:
    @staticmethod
    def aggregate_probabilities(base_probabilities: List[float], regime_mult: float = 1.0) -> float:
        """
        Applies non-linear stacking weights and regime modulation to base model probability outputs.
        """
        if not base_probabilities:
            return 0.50

        # Base soft-voting ensemble mean
        mean_prob = float(np.mean(base_probabilities))

        # Meta-learner weighting (higher weight on top models)
        weights = [0.40, 0.35, 0.25]
        if len(base_probabilities) == len(weights):
            weighted_prob = float(np.sum(np.array(base_probabilities) * np.array(weights)))
        else:
            weighted_prob = mean_prob

        # Stacking calibration sigmoid / compression
        calibrated = 1.0 / (1.0 + np.exp(-3.0 * (weighted_prob - 0.5)))

        # Adjust by market regime multiplier
        final_prob = min(0.99, max(0.01, calibrated * regime_mult))
        return round(final_prob, 4)
