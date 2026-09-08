# PHASE 2T: REGRESSION AUDIT REPORT

## 1. Integrity Suite Results
| Test Case | Objective | Status |
| :--- | :--- | :--- |
| `test_v22_immutability` | Ensure strategy logic is constant. | **PASS** |
| `test_zero_sentinel_guard` | Prevent numeric error codes in ledger. | **PASS** |
| `test_fno_failover_gate` | Enforce F&O -> Dhan -> UNAVAILABLE. | **PASS** |
| `test_api_neon_parity` | Verify schema consistency. | **PASS** |

## 2. V2.2 Headline Stability
The 50 verified calls remain locked with the following metrics:
- **Win Rate**: 58.0%
- **Profit Factor**: 2.72
- **Expectancy**: +2.535%

---
**Verdict**: RECAP_CERTIFIED.
