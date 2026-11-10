# Phase 4.3.2 Quality Gate Source Audit Report

**Date**: 2026-11-03  
**Target File**: [backend/services/signal_quality_service.py](file:///D:/TradeMindAI/backend/services/signal_quality_service.py)  
**Status**: **STRICT FAIL-CLOSED ENFORCED**

## Source Code Audit & Quality Policy

```python
@staticmethod
def should_publish(horizon: str, model: Optional[ModelMetadata], calibrated_prob: float) -> bool:
    """
    Strict fail-closed hard gate for signal publication.
    Unregistered model metadata (model is None) unconditionally returns False.
    """
    if not model:
        return False

    hp = model.hyperparameters or {}
    test_size = hp.get("test_size", 0)
    positives = hp.get("positives_test", 0)

    if test_size < 20:
        return False

    if horizon == "LONG":
        if model.roc_auc <= 0.65 or positives < 5 or (model.accuracy == 0.5 and model.roc_auc == 0.5):
            return False

    if horizon == "SWING" and model.roc_auc <= 0.52:
        return False

    if calibrated_prob < 0.52:
        return False

    return True
```

- **Remediation Result**: Removed loose probability-only fallback. Unregistered model metadata (`model is None`) unconditionally fails closed.
