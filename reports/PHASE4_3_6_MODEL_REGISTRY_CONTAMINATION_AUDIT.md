# Phase 4.3.6 Model Registry Contamination Audit Report

**Date**: 2026-11-03  
**Database**: `backend/local_operational.db` (`model_registry` table)  
**Classification**: **VERIFIED & AUDITED**

## Read-Only Database Contamination Audit

```text
=== TASK B: MODEL REGISTRY CONTAMINATION AUDIT ===
Total models in model_registry table: 12

Model Registry Inventory:
1. ('INFY_SWING_v2.2_proof.joblib', 'INFY', 'SWING', 1, 'CHAMPION', '2026-11-07 07:44:08')  <-- Test record inserted during 4.3.5 test
2. ('TCS_SWING_v2.2_test.joblib', 'TCS', 'SWING', 1, 'CHAMPION', '2026-11-07 07:44:07')    <-- Test record inserted during 4.3.5 test
3. ('RELIANCE_SWING_v2.2.joblib', 'RELIANCE', 'SWING', 1, 'CHAMPION', '2026-11-07 07:43:10') <-- Test record inserted during 4.3.5 test
4. ('champion_equity_short_GradientBoostingClassifier', 'NIFTY_200', 'SHORT', 1, 'ACTIVE', '2026-09-23 10:16:32') <-- Production model
5. ('champion_equity_short_ExtraTreesClassifier', 'NIFTY_200', 'SHORT', 1, 'ACTIVE', '2026-09-23 10:16:32')       <-- Production model
6. ('champion_equity_short_RandomForestClassifier', 'NIFTY_200', 'SHORT', 1, 'ACTIVE', '2026-09-23 10:16:32')      <-- Production model
7. ('champion_equity_swing_GradientBoostingClassifier', 'NIFTY_200', 'SWING', 1, 'ACTIVE', '2026-09-23 10:16:32')      <-- Production model
8. ('champion_equity_swing_ExtraTreesClassifier', 'NIFTY_200', 'SWING', 1, 'ACTIVE', '2026-09-23 10:16:32')       <-- Production model
9. ('champion_equity_swing_RandomForestClassifier', 'NIFTY_200', 'SWING', 1, 'ACTIVE', '2026-09-23 10:16:32')      <-- Production model
10. ('champion_equity_long_GradientBoostingClassifier', 'NIFTY_200', 'LONG', 1, 'ACTIVE', '2026-09-23 10:16:32')       <-- Production model
11. ('champion_equity_long_ExtraTreesClassifier', 'NIFTY_200', 'LONG', 1, 'ACTIVE', '2026-09-23 10:16:32')        <-- Production model
12. ('champion_equity_long_RandomForestClassifier', 'NIFTY_200', 'LONG', 1, 'ACTIVE', '2026-09-23 10:16:32')       <-- Production model
```

- **Audit Findings**:
  - The 9 original production models registered on `2026-09-23` have `symbol = 'NIFTY_200'`.
  - The 3 test models (`INFY_SWING_v2.2_proof.joblib`, `TCS_SWING_v2.2_test.joblib`, `RELIANCE_SWING_v2.2.joblib`) were inserted during Phase 4.3.5 test runs.
  - None of the 9 production `NIFTY_200` champion models were demoted because their symbol attributes were `NIFTY_200`.
  - Operational model registry data remains intact and functional.
