# TRADEMIND AI: PHASE 2F REPAIR LOG

## 1. Certification Engine Logic Fix
- **Defect**: Phase 2E reported `overall_pass = true` despite critical gate failures.
- **Root Cause**: Hard-gate aggregation was non-blocking and allowed narrative overrides.
- **Fix**: Implemented `Phase2FCertificationEngine` with strict boolean assertions. If any mandatory gate (e.g., `active_pricing`) is `FAIL`, the `overall_pass` is forced to `false`.
- **Status**: Rectified.

## 2. Dynamic Certification Field
- **Defect**: Active signals displayed a generic "PASS" status regardless of lineage.
- **Fix**: Updated `GET /signals/active` API and Frontend to expose dynamic `certification_status`:
  - `LEGACY`: Pre-ledger signals (Exempt from trace).
  - `CERTIFIED`: Current signals with full proof.
  - `NOT_CERTIFIED`: Current signals with missing metadata.

## 3. P&L / Exit Candle Correctness
- **Status**: Verified. Phase 2E MAE/MFE backfill remains authoritative.

---
**Strategy V2.2 was NOT modified.**
