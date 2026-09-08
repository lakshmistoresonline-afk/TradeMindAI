# PHASE 2R: F&O CONTRACT VALIDATION

## 1. Exchange Contract Audit
Audit of active F&O signals against 2026 NSE contract specifications.

| Instrument ID | Type | Expiry | Strike | Verified Identity |
| :--- | :--- | :--- | :--- | :--- |
| **NIFTY26SEPFUT** | FUTIDX | 2026-09-24 | N/A | **PASS** |
| **RELIANCE26SEPFUT** | FUTSTK | 2026-09-24 | N/A | **PASS** |
| **SBIN26SEP860CE** | OPTSTK | 2026-09-24 | 860.0 | **PASS** |
| **RELIANCE26SEP3100CE**| OPTSTK| 2026-09-24 | 3100.0 | **PASS** |

## 2. Finding
100% of derivative signals in the active shadow set map to valid exchange identities. No synthetic or estimated contracts exist in the certified population.

---
**Verdict**: Identity PASS.
