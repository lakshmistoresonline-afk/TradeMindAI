# DASHBOARD FIREBASE MAPPING

## Firestore Project
**Project ID:** `com-webcraft-trademindai-c8f75`

## Collection Mapping

### 1. `shadow_summary/latest`
Used for global dashboard stats and system health.

| Dashboard Field | Firestore Field | Notes |
| :--- | :--- | :--- |
| BASELINE START | `baseline_start` | Read directly from Firestore. |
| LAST DATA SYNC | `last_run` | Timestamp of last engine execution. |
| EVALUATION CYCLES | `evaluation_cycles` | Total cycles since baseline. |
| EVALUATION EVENTS | `evaluation_events` | Total symbols evaluated. |
| COMPLETED TRADES | `trade_count` | Count of resolved signals. |
| WIN RATE | `win_rate` | Win rate % of resolved signals. |
| MARKET STATUS | `market_status` | OPEN / CLOSED based on IST. |

### 2. `shadow_signals` (Collection)
Used for the "ACTIVE SIGNALS" table.

| Dashboard Field | Firestore Field | Filter |
| :--- | :--- | :--- |
| SYMBOL | `symbol` | `status == 'ACTIVE'` |
| DIRECTION | `direction` | `status == 'ACTIVE'` |
| ENTRY | `entry_price` | `status == 'ACTIVE'` |
| PROB | `prob` | `status == 'ACTIVE'` |
| EV | `ev` | (Calculated from prob/target/stop) |
| STATUS | `status` | `status == 'ACTIVE'` |

### 3. `shadow_scan_diagnostics` (Collection)
Used for the "UNIVERSE SCAN AUDIT" table.

- **Query:** Order by `scan_timestamp` DESC, limit 200.
- **Mapping:**
    - `symbol` -> `symbol`
    - `decision` -> `decision`
    - `rejection_reason` -> `reason`
    - `probability` -> `score`
    - `model_version` -> `model_version`

## Sync Logic
- Authoritative source for all dashboard metrics is **Firestore**.
- No hardcoded mocks are allowed.
- Zero is a valid value.
