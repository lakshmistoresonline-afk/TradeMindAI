# PHASE 2S: F&O CONTRACT VALIDATION

## 1. Exchange Contract Audit
Audit of active shadow signals against documented 2026 NSE contract specifications.

| Instrument ID | Type | Expiry | Strike | Verified |
| :--- | :--- | :--- | :--- | :--- |
| **NIFTY26SEPFUT** | FUTIDX | 2026-09-24 | N/A | **PASS** |
| **RELIANCE26SEPFUT** | FUTSTK | 2026-09-24 | N/A | **PASS** |
| **SBIN26SEP860CE** | OPTSTK | 2026-09-24 | 860.0 | **PASS** |
| **RELIANCE26SEP3100CE**| OPTSTK| 2026-09-24 | 3100.0 | **PASS** |

## 2. Finding
100% of derivative signals in the active shadow set map to valid exchange identities. No synthetic or estimated contracts were found in the population.

---
**Verdict**: Identity PASS.
