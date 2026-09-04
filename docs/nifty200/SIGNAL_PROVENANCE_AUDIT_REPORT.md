# TRADEMIND AI: SIGNAL PROVENANCE AUDIT REPORT

## 1. Provenance Coverage
- **Total Unique Calls**: 1,259
- **New Strategy V2.2 Coverage**: 100%
- **Legacy Population Coverage**: 0% (Documented Limitation)

## 2. Integrity Controls
- [x] **Input Hashing**: Every new signal captures a SHA-256 hash of its input feature vector.
- [x] **Decision Hashing**: Logical decisions are linked to immutable signal IDs.
- [x] **Temporal Snapshots**: Source data timestamps are preserved at T-0.

## 3. Findings
All signals generated since the implementation of Ledger 2.0 (RC-7E) carry full provenance metadata. Legacy records have been migrated with `provenance_id = UNAVAILABLE` to preserve historical truth.

---
**Verdict**: PROVENANCE_ACTIVE
