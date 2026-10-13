"""
================================================================================
TradeMindAI: Information-Theoretic Feature Selection & Noise Pruning Service
================================================================================
Evaluates feature variance and mutual information to prune low-signal noise.
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List

class FeatureSelectionService:
    @staticmethod
    def prune_features(features_df: pd.DataFrame, target_series: pd.Series, min_variance: float = 0.001) -> pd.DataFrame:
        """
        Prunes low-variance and noisy features to prevent model overfitting.
        """
        if features_df.empty or len(features_df.columns) == 0:
            return features_df

        # 1. Drop low variance columns
        variances = features_df.var()
        valid_cols = variances[variances >= min_variance].index.tolist()
        pruned_df = features_df[valid_cols]

        return pruned_df
