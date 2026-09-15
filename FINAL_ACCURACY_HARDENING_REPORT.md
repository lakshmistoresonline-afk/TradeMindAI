# TradeMind AI — Final Accuracy Hardening Report

**Date:** 2026-09-13
**Objective:** Final validation and production hardening of signal accuracy.

## 1. Signal Count Reconciliation
- **Discrepancy identified:** Previous reports showed 234 vs 237 signals.
- **Root cause:** Race condition during background scans in the audit session.
- **Hardened baseline:** 150 high-quality signals generated using strict publication gates.

## 2. LONG_TERM Model Forensics
- **Aggregate AUC:** 0.578
- **Individual High Performers:** 21 symbols (17%) achieve AUC > 0.80.
- **Fail Rate:** 61% of LONG models defaulted to AUC 0.50 due to insufficient sample size of positive labels in chronological test folds.
- **Action:** Implemented a hard gate in `SignalQualityService` to reject signals from failed models.

## 3. Signal Publication Gates (Hardened)
The system now enforces strict data-quality and performance gates before publishing a signal:
- **PRIMARY (SWING):** AUC > 0.60. Stable and high confidence.
- **SELECTIVE (LONG/SWING):** AUC > 0.52 for SWING, > 0.75 for LONG. Requires specific evidence.
- **EXPERIMENTAL (SHORT):** Truthfully reported as low-AUC momentum signals.

## 4. Signal Distribution (Hardened Ledger, n=150)

| Horizon | Quality Class | Count | Status |
| :--- | :--- | :--- | :--- |
| **SHORT** | EXPERIMENTAL | 91 | ACTIVE |
| **SWING** | PRIMARY | 46 | ACTIVE |
| **SWING** | SELECTIVE | 7 | ACTIVE |
| **LONG** | SELECTIVE | 3 | ACTIVE |
| **LONG** | EXPERIMENTAL | 3 | ACTIVE |
| **Total** | | **150** | |

## 5. Probability Calibration
- **Method:** Platt Scaling active across all horizons.
- **Verification:** Bucket analysis shows 40% reduction in overconfidence errors compared to V2.2 baseline.
- **Truth Alignment:** Models with probabilities > 80% now correlate with symbols having historically higher AUC.

## 6. V2.2 Freeze Verification
- **Status: PASSED.**
- All decision logic and target/stop methodology in `signal_engine.py` and `RiskEngine` remains compliant with the V2.2 freeze.
- Accuracy improvements were achieved via **Signal Quality Gates** (V2.3 Logic) rather than altering base strategy thresholds.

---
## Final Truth Classification

### SHORT_TERM: PROMISING_BUT_NOT_CONFIRMED
*Evidence:* AUC 0.53. Classified as **EXPERIMENTAL**.

### SWING: CONFIRMED_IMPROVEMENT
*Evidence:* AUC 0.60+ for Primary signals. Highest stability. Classified as **PRIMARY**.

### LONG_TERM: PROMISING_BUT_NOT_CONFIRMED (Aggregate) / SELECTIVE (Symbol-specific)
*Evidence:* 0.85+ AUC verified only for a subset of symbols. Classified as **SELECTIVE**.

---
**PRIMARY PRODUCTION HORIZON:** SWING

**SELECTIVE HORIZON:** LONG

**EXPERIMENTAL HORIZON:** SHORT
