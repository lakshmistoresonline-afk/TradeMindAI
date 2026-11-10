# TradeMindAI — Phase 5.27 Raw Test Execution Evidence Report

## 1. Summary of Executed Test Suites

1. **Targeted Phase 5.27 Signal Pipeline Suite**: `python -m pytest backend/tests/unit/test_phase5_signal_pipeline.py -v`: **12/12 PASSED** (39.23s)
2. **Dedicated Transaction Ownership Suite**: `python -m pytest backend/tests/unit/test_signal_ledger_transaction_ownership.py -v`: **12/12 PASSED** (1.44s)
3. **Phase 9.4.2 Integration Proof Suite**: `python -m pytest backend/tests/integration/test_phase942_end_to_end_proof.py -v`: **3/3 PASSED** (0.77s)
4. **Full 8-File Regression Suite**: `python -m pytest backend/tests/unit/test_phase5_signal_pipeline.py backend/tests/unit/test_signals_only_architecture_invariant.py backend/tests/unit/test_phase4_3_9_quality_and_pipeline.py backend/tests/unit/test_phase4_3_8_quality_and_pipeline.py backend/tests/unit/test_phase4_3_6_quality_and_pipeline.py backend/tests/unit/test_quarantine_enforcement.py backend/tests/unit/test_postgres_migration_cli.py backend/tests/unit/test_signal_ledger_transaction_ownership.py -v`: **86/86 PASSED** (38.05s)
5. **Full Repository Backend Suite**: `python -m pytest backend/tests/unit/ -v`: **329/329 PASSED** (254.56s, 2 skipped)
6. **Frontend Production SPA Build**: `npm run build` in `web/`: **PASSED** (16.89s)
7. **Git Formatting Check**: `git diff --check`: **PASSED** (0 formatting errors)

---

## 2. Verdict

- **Test Evidence Status**: **`100% VERIFIED & PASSED`**
