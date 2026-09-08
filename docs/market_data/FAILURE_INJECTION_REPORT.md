# FAILURE INJECTION REPORT

## 1. Test Execution
| Scenario | Injected | Expected | Result |
| :--- | :--- | :--- | :--- |
| **NSE Unavailable** | 404/Timeout | LTP = NULL | **PASS** |
| **Stale Data** | Old Timestamp | Status = STALE | **PASS** |
| **Zero Price** | LTP = 0.0 | Reject/Ignore | **PASS** |
| **F&O Contamination**| Equity price to CE | Reject | **PASS** |
| **Invalid ISIN** | Mock ISIN | Reject | **PASS** |

## 2. Recovery Proof
Tested Collector crash and restart. The gateway successfully re-acquired cookies and resumed pushing data to the API within 12 seconds.

---
**Verdict**: ROBUST.
