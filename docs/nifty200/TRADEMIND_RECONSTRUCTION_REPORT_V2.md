# TRADEMIND AI: RECONSTRUCTION REPORT (V2)

## 1. Scope
Forensic reconstruction was performed on all 50 verified signals in the Phase 6 shadow set. Each signal's outcome was independently determined using 1-minute OHLC data.

## 2. Re-Verification Results
| Metric | Stored | Reconstructed | Status |
| :--- | :--- | :--- | :--- |
| **Total Outcomes** | 50 | 50 | **MATCH** |
| **Target Hits** | 29 | 29 | **MATCH** |
| **Stop Losses** | 20 | 20 | **MATCH** |
| **Timeouts** | 1 | 1 | **MATCH** |

## 3. P&L Forensics
All 50 signals were recalculated using the canonical `PNLEngine` (0.20% friction).
- **Match Rate**: 100% (after SBIN repair).
- **Rounding Delta**: < 0.001% aggregate.

## 4. Look-Ahead Audit
Re-audited 100% of the verified dataset for temporal isolation.
- **Signal -> Outcome Delay**: entry timestamp < exit timestamp verified for all records.
- **Data Freshness**: No signal used prices published after its `created_at` timestamp.

---
**Verdict**: RECONSTRUCTION_VERIFIED
