# TradeMind AI: Final Population Reconciliation

## 1. Authoritative Denominators (2026-09-17)
Verified from Neon PostgreSQL authoritative ledger:

| Population | Count | Methodology |
| :--- | :--- | :--- |
| **Historical Signals** | 50 | Total closed calls in ledger |
| **Resolved Outcomes** | 49 | Binary outcomes (Wins + Losses) |
| **Timeouts** | 1 | Excluded from Win-Rate Denominator |

## 2. Outcome Distribution
- **TARGET_HIT**: 29
- **STOP_LOSS**: 20
- **TIMEOUT**: 1
- **OTHER**: 0

## 3. Reconciliation Logic
- **Win Rate**: 29 / 49 = **59.18%**
- **Profit Factor**: Sum(Wins) / Sum(Losses) = **2.73**
- **Consistency**: 100% of signals in the ledger are accounted for in the aggregate metrics.

---
**Verdict**: **PASS**
All performance metrics on the platform trace directly to these 50 immutable historical records.
