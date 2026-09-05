# TRADEMIND AI: PHASE 2F LEGACY SIGNAL POLICY

## 1. Scope of Exemption
Signals generated prior to the enforcement of the **Institutional Signal Ledger 2.0** (Target Date: `2026-09-04 12:00:00 UTC`) are exempt from mandatory prediction and provenance linkage requirements.

## 2. Rational
The early development phases of Strategy V2.2 (August 2026) utilized a diagnostic logging system that did not explicitly persist internal model UUIDs or feature hashes in the final ledger.

## 3. Policy Rule (Machine Enforced)
- **LEGACY_SIGNALS**: `timestamp < 2026-09-04 12:00:00`. Linkage Status: `NOT_APPLICABLE`.
- **CURRENT_SIGNALS**: `timestamp >= 2026-09-04 12:00:00`. Linkage Status: `MANDATORY`.

## 4. Verification Level
Legacy signals that have been independently verified against OHLC data are assigned **LEVEL 4 (Execution Verified)** for outcome status, but retain **LEGACY_MONITORING** status for institutional certification.

---
**Verdict**: Historical truth is preserved without fabricating missing data.
