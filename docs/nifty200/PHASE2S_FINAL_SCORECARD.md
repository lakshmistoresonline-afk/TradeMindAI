# TRADEMIND AI: PHASE 2S — FINAL INSTITUTIONAL SCORECARD

| Gate | Status | Mandatory | Blocking | Reason |
| :--- | :--- | :--- | :--- | :--- |
| population_integrity | **PASS** | YES | NO | PASS |
| v22_freeze | **PASS** | YES | NO | PASS |
| instrument_master | **FAIL** | YES | YES | No instruments found in Neon for provider Upstox. Sync required. |
| upstox_authentication | **CONFIGURATION_REQUIRED** | YES | YES | UPSTOX_ANALYTICS_TOKEN missing. |
| dhan_authentication | **CONFIGURATION_REQUIRED** | YES | YES | DHAN_ACCESS_TOKEN missing. |
| provider_activation | **CONFIGURATION_REQUIRED** | YES | YES | All F&O providers unauthenticated. Credentials required for activation. |
| fno_identity | **PASS** | YES | NO | PASS |
| fno_quote_retrieval | **CONFIGURATION_REQUIRED** | YES | YES | Authentication missing for live F&O premium retrieval. |
| fno_derivative_pricing | **CONFIGURATION_REQUIRED** | YES | YES | Authentication missing for live F&O premium retrieval. |
| price_freshness | **DATA_UNAVAILABLE** | YES | YES | Institutional activation gate reason required. |
| underlying_derivative_separation | **PASS** | YES | NO | PASS |
| failover | **PASS** | YES | NO | PASS |
| neon_authority | **PASS** | YES | NO | PASS |
| firestore_mirror | **PASS** | YES | NO | PASS |
| api_parity | **PASS** | YES | NO | PASS |
| dashboard_runtime | **PASS** | YES | NO | PASS |
| websocket_runtime | **NOT_APPLICABLE** | YES | NO | WebSocket requires live authentication. |
| security | **PASS** | YES | NO | PASS |
| failure_injection | **PASS** | YES | NO | PASS |
| audit_reconciliation | **PASS** | YES | NO | PASS |
