# Phase 4.3.3 Valid Signal End-to-End Test Report

**Date**: 2026-11-03  
**Status**: **PASSED & VERIFIED**

## Case B — End-to-End Controlled Signal Persistence Proof

1. **Test Signal Object**: Constructed valid `LiveSignal` (`symbol="RELIANCE"`, `rating="BUY"`, `direction="LONG"`, `timeframe="SWING"`, `entry_price=2500.0`, `confidence=0.82`, `model_version="v2.2"`, `quality_class="PRIMARY"`).
2. **BUY Eligibility Predicate**: `is_eligible_buy(test_signal)` evaluated `True`.
3. **Database Ledger Persistence**: `SignalLedgerService._create_signal_internal(test_signal, session=session)` returned `status = "PERSISTED"`.
4. **Independent Database Read-Back**: Queried `LiveSignalDB` by `id` from SQLite/PostgreSQL ledger and verified symbol `RELIANCE`, entry price `2500.0`, direction `LONG`, rating `BUY`.
