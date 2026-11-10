# Phase 4.3.8 Historical Model Registry Reconciliation Report

**Date**: 2026-11-03  
**Database**: `D:\TradeMindAI\backend\local_operational.db`  
**Classification**: **PARTIAL — HISTORICAL BASELINE UNRESOLVED**

## Historical Registry Status

- **9 Production Champion Models (Registered 2026-09-23)**: Registered under `symbol = 'NIFTY_200'` across `SHORT`, `SWING`, and `LONG` horizons (`GradientBoostingClassifier`, `ExtraTreesClassifier`, `RandomForestClassifier`). All 9 remain `is_champion = True` and active.
- **3 Test Records (Inserted 2026-11-07)**: `INFY_SWING_v2.2_proof.joblib`, `TCS_SWING_v2.2_test.joblib`, `RELIANCE_SWING_v2.2.joblib` inserted during earlier test runs.
- **Verdict**: Per Section 6 & 14 rules, because original model state prior to test insertion cannot be proven from available database logs, historical status is classified as `PARTIAL — SAFETY OR HISTORICAL BASELINE EVIDENCE INCOMPLETE`.
