# MARKET DATA COLLECTION RUN REPORT

## 1. Run Summary
| Source | Requested | Received | Failed | Success Rate |
| :--- | :--- | :--- | :--- | :--- |
| **NSE Equity** | 200 | 198 | 2 | 99.0% |
| **NSE F&O** | 10 | 10 | 0 | 100.0% |
| **Yahoo Ref** | 50 | 50 | 0 | 100.0% |

## 2. Blockers
Occasional `403 Forbidden` errors from NSE when request frequency exceeds 1 per second. Automated backoff and jitter resolved these in subsequent retries.

---
**Status**: OPERATIONAL.
