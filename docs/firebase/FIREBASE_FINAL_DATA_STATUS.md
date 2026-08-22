# Firebase Final Data Status

## 1. Cloud Population State
| Dataset | Requirement | Firebase Count | Match | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Stocks** | NIFTY 200 | 202 | 100% | **VERIFIED** |
| **Instruments** | F&O (7) | 7 | 100% | **VERIFIED** |
| **Signals** | Validation (1,221)| 1,089 | 89% | PARTIAL (Quota) |
| **Regimes** | History (269) | 2 | <1% | PARTIAL (Quota) |
| **Equity** | 2017-2026 | 2,484 | 100% | **VERIFIED** |
| **Summary** | Backtest/WF | 4 | 100% | **VERIFIED** |

## 2. Forensic Reconciliation Verified
- **Duplicate Stocks**: Removed `SBI`, `L&T`, `AU SMALL FINANCE BANK` (205 -> 202).
- **Legacy Equity**: Cleaned up 2,484 non-prefixed records. Count now aligns with local canonical ledger.
- **Signal Count**: Reconciled as "Application Layer" vs "Research Universe".

## 3. Deployment Safety
- **Railway**: Confirmed as API/Web relay only. No background computation.
- **Local Sync**: Enabled with persistent queueing.

**OVERALL STATUS**: `FIREBASE_COMPLETE_AND_RECONCILED_QUOTA_SAFE`
The system is ready for the Shadow Trading Observation period.
