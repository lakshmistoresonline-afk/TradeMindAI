# PHASE 2P: IMPLEMENTATION FORENSIC AUDIT

## 1. Code-Level Defect Matrix
| Component | Status | Identified Defects |
| :--- | :--- | :--- |
| **UpstoxProvider** | **PARTIAL** | `get_ltp` returns `None` on failure (correct) but still uses `NSE_EQ|` heuristic for F&O if resolution fails. |
| **DhanProvider** | **PARTIAL** | `get_ltp` returns `None` on failure. Numerical `SecurityId` mapping is still heuristic (assumes symbol is ID). |
| **InstrumentMasterService** | **FUNCTIONAL** | Basic SQLAlchemy resolution implemented. Needs integration into provider LTP paths. |
| **PriceResolver** | **HARDENED** | Failover sequence implemented. Anti-contamination guard present. |
| **WebSocket** | **MISSING** | `subscribe_live` methods are placeholders with print statements only. No real processing. |

## 2. Forensic Discovery (Hidden Sentinels)
While Phase 2O used -1.0/-2.0, the current code in `upstox_provider.py` still contains:
```python
return -1.0 # AUTH_REQUIRED (Line 54)
return -2.0 # INSTRUMENT_NOT_FOUND (Line 66)
```
These **MUST** be removed in favor of `None` to prevent numeric pollution of the signal ledger.

## 3. Persistent Blockers
- **Authentication**: `UPSTOX_ANALYTICS_TOKEN` and `DHAN_ACCESS_TOKEN` are missing in the local environment, blocking live LTP retrieval.
- **Instrument Master Data**: The Neon `instruments` table needs to be populated with current 2026 contracts to enable resolution.

---
**Verdict**: Infrastructure is **Audit-Ready** but **Operational-Blocked** by numeric sentinels and missing master data.
