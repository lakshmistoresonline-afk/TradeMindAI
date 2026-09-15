from typing import Dict, Any, Optional, List
from backend.domain.models.data_platform import ModelMetadata
from backend.domain.models.ios import LiveSignal

class SignalQualityService:
    """
    Phase 11: Signal Quality & Publication Gates.
    Determines Quality Class and enforces sample size requirements.
    """

    MIN_SAMPLES_PRIMARY = 100
    MIN_POSITIVES_PRIMARY = 20

    @staticmethod
    def get_quality_class(horizon: str, model: Optional[ModelMetadata]) -> str:
        """
        Determines the quality classification for a signal.
        PRIMARY, SELECTIVE, EXPERIMENTAL.
        """
        if not model:
            return "EXPERIMENTAL"

        hp = model.hyperparameters or {}
        test_size = hp.get("test_size", 0)
        positives = hp.get("positives_test", 0)

        # 1. PRIMARY Gate (Most Robust)
        if horizon == "SWING" and model.roc_auc > 0.60 and test_size >= 50 and positives >= 10:
            return "PRIMARY"

        # 2. SELECTIVE Gate (Qualified but specialized)
        if horizon == "LONG" and model.roc_auc > 0.70 and test_size >= 30 and positives >= 5:
            return "SELECTIVE"
        if horizon == "SWING" and model.roc_auc > 0.55:
            return "SELECTIVE"

        return "EXPERIMENTAL"

    @staticmethod
    def should_publish(horizon: str, model: Optional[ModelMetadata], calibrated_prob: float) -> bool:
        """
        Hard gate for signal publication.
        """
        if not model:
            return False

        hp = model.hyperparameters or {}
        test_size = hp.get("test_size", 0)
        positives = hp.get("positives_test", 0)

        # Minimum Data Visibility Rule
        if test_size < 20:
            return False

        # 1. LONG_TERM Gate: Requires high AUC and sufficient evidence
        if horizon == "LONG":
            if model.roc_auc <= 0.65:
                return False
            if positives < 5:
                return False
            if model.accuracy == 0.5: return False # Failed model

        # 2. SWING Gate:
        if horizon == "SWING":
            if model.roc_auc <= 0.52:
                return False

        # 3. Probability Gate
        if calibrated_prob < 0.52:
            return False

        return True
