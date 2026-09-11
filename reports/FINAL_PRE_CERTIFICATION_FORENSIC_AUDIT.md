# Final Pre-Certification Forensic Audit - TradeMind AI

## Audit Summary
This audit was performed on 2026-09-11 to identify architectural inconsistencies, data integrity risks, and legacy code prior to final production certification.

## Findings

### 1. Legacy AI Baking Logic
- **File**: `app/src/main/java/com/webcraft/trademindai/BakingScreen.kt`
- **Severity**: Low (Android specific)
- **Impact**: Leftover boilerplate from a "Baking App" template. Includes strings and logic for recipes.
- **Recommended Action**: Remove or isolate as non-production code. Permitted under V2.2 freeze.

### 2. Hardcoded Fundamental Analysis in Android UI
- **File**: `app/src/main/java/com/webcraft/trademindai/ui/screens/StockDetailScreen.kt`
- **Line**: 37
- **Severity**: Medium
- **Impact**: Displays "PE Ratio: 25, Intrinsic Value: ₹1500" for all stocks. MISLEADING.
- **Recommended Action**: Replace with API-driven data. Permitted under V2.2 freeze.

### 3. Hardcoded Observation Labels in Web Accuracy Page
- **File**: `web/src/pages/Accuracy.tsx`
- **Line**: 87
- **Severity**: Low
- **Impact**: Mentions "(n=50)" in an alert box. This should be dynamic.
- **Recommended Action**: Link to real population count from API. Permitted under V2.2 freeze.

### 4. Duplicate Signal Pipelines
- **File**: `backend/services/signal_auditor.py` vs `backend/services/signal_lifecycle_service.py`
- **Severity**: Medium
- **Impact**: Multiple ways to audit/transition signals. Potential for logic drift.
- **Recommended Action**: Consolidate into `SignalLifecycleService`. Permitted under V2.2 freeze.

### 5. Probability Fallback Logic
- **File**: `backend/services/signal_engine.py`
- **Line**: 86
- **Severity**: Medium
- **Impact**: Fallback to 0.5 probability when metadata is missing. Audited but still a fallback.
- **Recommended Action**: Ensure all inference calls return metadata. Permitted under V2.2 freeze.

### 6. R:R Derived Representation
- **File**: `backend/services/signal_engine.py`
- **Severity**: Low
- **Impact**: R:R is calculated and stored. If target/stop are modified (which they shouldn't be), R:R must be consistent.
- **Recommended Action**: Add independent recalculation in certification engine.

### 7. Model Coverage Discrepancy
- **Status**: 101/202 symbols covered.
- **Severity**: High (Data Status)
- **Impact**: 50% of the NIFTY-200 universe is not tradeable by the AI.
- **Recommended Action**: Verify if this is due to data insufficiency (Phase 9-10).

## V2.2 Freeze Status
The files mentioned in `V22_FREEZE_MANIFEST.json` are:
- `backend/services/signal_engine.py`
- `backend/services/outcome_engine.py`
- `backend/services/risk_engine.py`
- `backend/core/risk.py`
- `backend/core/config.py`

Any changes to these files to fix reporting or data ingestion must be handled with extreme care to not alter the deterministic decision logic.
