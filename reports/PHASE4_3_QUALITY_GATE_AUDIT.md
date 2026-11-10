# Phase 4.3 Quality Gate Audit Report

**Date**: 2026-11-03  
**Target File**: [backend/services/signal_quality_service.py](file:///D:/TradeMindAI/backend/services/signal_quality_service.py)

## Quality Gate Publication Policy

- **Calibrated Probability Requirement**: Requires `calibrated_prob >= 0.52`.
- **Unregistered Model Metadata Fallback**: When `model` metadata is un-registered in `model_metadata` table, high-conviction probability (`calibrated_prob >= 0.52`) allows publishing cleanly.
- **Sample Size Check**: When model metadata is present, `test_size >= 20` and `roc_auc > 0.52` are enforced.
