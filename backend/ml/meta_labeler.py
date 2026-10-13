"""
Meta-Labeling Model Pipeline (Prado Methodology)
Trains a secondary classifier (LightGBM/XGBoost or Random Forest) to evaluate
whether primary signal model outputs will be profitable, filtering false breakouts.
"""

import os
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from typing import Dict, Any, Tuple

class MetaLabeler:
    def __init__(self, registry_path: str = "backend/ml/registry"):
        self.registry_path = registry_path
        os.makedirs(self.registry_path, exist_ok=True)
        self.model = None

    def fit(self, X: pd.DataFrame, y: pd.Series, symbol: str, direction: str) -> str:
        """
        Trains secondary meta-model on primary features, volatility, and order flow metrics.
        y should be 1 if primary signal was profitable (hit TP before SL), 0 otherwise.
        """
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=6,
            random_state=42,
            n_jobs=-1
        )
        self.model.fit(X, y)

        filename = f"{symbol}_{direction}_meta_model.joblib"
        filepath = os.path.join(self.registry_path, filename)
        joblib.dump(self.model, filepath)
        return filepath

    def predict_probability(self, features: pd.DataFrame, symbol: str, direction: str) -> float:
        """
        Returns the probability (0.0 to 1.0) that the primary signal will succeed.
        """
        if self.model is None:
            filename = f"{symbol}_{direction}_meta_model.joblib"
            filepath = os.path.join(self.registry_path, filename)
            if os.path.exists(filepath):
                self.model = joblib.load(filepath)
            else:
                # Fallback default probability if no meta-model trained yet
                return 0.75

        try:
            probs = self.model.predict_proba(features)
            return float(probs[0][1]) # probability of success class 1
        except Exception as e:
            print(f"MetaLabeler prediction error: {e}")
            return 0.70
