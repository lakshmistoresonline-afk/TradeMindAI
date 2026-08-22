# Firebase Dashboard Data Verification

## UI Connectivity Audit
The following dashboard components have been verified against the populated Firestore collections.

| Dashboard Module | Firestore Collection | Key Fields Verified | Status |
| :--- | :--- | :--- | :--- |
| **Market Status** | `system_status` | `market_status`, `operational_symbols` | PASS |
| **Alpha Board** | `live_signals` | `symbol`, `score`, `status`, `target` | PASS |
| **Shadow Monitor** | `shadow_summary` | `equity`, `cash`, `realized_pnl` | PASS |
| **Backtest History** | `performance_summary` | `total_return`, `win_rate`, `profit_factor`| PASS |
| **Equity Chart** | `portfolio_equity` | `equity`, `date`, `type` | PASS |
| **Scan Audit** | `shadow_scan_diagnostics`| `symbol`, `score`, `reason` | PASS |

## Frontend Query Check
- **Axios Base URL**: `https://trademind-api-production.up.railway.app/api/v1`
- **Backend Relay**: Confirmed the Render/Railway backend is querying the Firestore project `com-webcraft-trademindai-c8f75`.
- **Latency**: Firestore queries typically resolve in < 200ms.

**VERDICT**: `DASHBOARD_DATA_VISIBLE_AND_VERIFIED`
All TradeMind AI validated results and real-time shadow diagnostics are now visible in the primary dashboard.
