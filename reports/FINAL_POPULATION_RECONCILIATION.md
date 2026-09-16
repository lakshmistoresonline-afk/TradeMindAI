# TradeMind AI: Final Population Reconciliation

## 1. Canonical Population Summary (2026-09-16)
Verified distribution across all authoritative Neon PostgreSQL ledgers:

| Population Metric | Count | Source |
| :--- | :--- | :--- |
| **PREDICTIONS** | 7,500 | `predictions` table (Scanned opportunities) |
| **INTERNAL_SIGNALS** | 166 | Sum of `live_signals` and `shadow_signals` |
| **PRODUCTION_SIGNALS**| 83 | Subtotal used for validation (33 Active + 50 History) |
| **ACTIVE** | 33 | `live_signals` (Waiting for entry/Active) |
| **HISTORICAL** | 50 | `shadow_signals` (Status != 'ACTIVE') |
| **RESOLVED** | 50 | Signals with terminal outcomes |

## 2. Transition Logic
| From | To | Difference | Reason |
| :--- | :--- | :--- | :--- |
| Predictions (7500) | Signals (166) | 7,334 | Filtered by Strategy V2.2 risk and quality gates. |
| Signals (166) | Production (83) | 83 | Signals excluded from production display (Research/Internal). |
| Historical (50) | Resolved (50) | 0 | 100% of historical production signals reached terminal state. |

## 3. Terminal Outcome Breakdown (N=50)
- **TARGET_HIT**: 29
- **STOP_LOSS**: 20
- **TIMEOUT**: 1
- **OTHER**: 0

---
**Verdict**: **PASS**
All populations are reconciled and traceable to unique `signal_id` records in Neon.
