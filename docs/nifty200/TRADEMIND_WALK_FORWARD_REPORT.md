# TRADEMIND AI: WALK-FORWARD VALIDATION REPORT

## 1. Validation Logic
The system enforces **Walk-Forward Validation** to ensure model stability across different market regimes.
- **Window Size**: 500 training days / 100 test days.
- **Step**: Rolling 100-day forward motion.
- **Leakage Guard**: Strict `test_start > train_end` boundary.

## 2. Dataset Versioning
- **Canonical Version**: `NIFTY_200_AUG2026`
- **Feature Version**: `v1.0.0` (11 core technical indicators)

## 3. Champion / Challenger Registry
New models are added to the registry as `CHALLENGER`s.
- **Promotion Gate**: Challenger must outperform Champion in both **Brier Score** and **Profit Factor** over a 20-trade window.
- **Manual Promotion**: No automatic champion replacement without explicit validation report.
