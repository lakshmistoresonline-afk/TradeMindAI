# TRADEMIND AI: PHASE 2Q — FINAL INSTITUTIONAL SCORECARD

| Gate | Status | Mandatory | Blocking | Reason |
| :--- | :--- | :--- | :--- | :--- |
| population_integrity | **PASS** | YES | NO | PASS |
| v22_freeze | **PASS** | YES | NO | PASS |
| instrument_master | **CONFIGURATION_REQUIRED** | YES | YES | No instruments found in Neon for provider Upstox. Sync required. |
| upstox_authentication | **CONFIGURATION_REQUIRED** | YES | YES | UPSTOX_ANALYTICS_TOKEN missing. |
| dhan_authentication | **CONFIGURATION_REQUIRED** | YES | YES | DHAN_ACCESS_TOKEN missing. |
| provider_activation | **CONFIGURATION_REQUIRED** | YES | YES | No authenticated F&O providers active. |
| fno_identity | **PASS** | YES | NO | PASS |
| fno_quote_retrieval | **CONFIGURATION_REQUIRED** | YES | YES | Authentication required for live F&O retrieval. |
| fno_derivative_pricing | **CONFIGURATION_REQUIRED** | YES | YES | Authentication required for live F&O retrieval. |
| price_freshness | **DATA_UNAVAILABLE** | YES | YES | Institutional reason required for non-PASS status. |
| underlying_derivative_separation | **PASS** | YES | NO | PASS |
| failover_logic | **PASS** | YES | NO | PASS |
| neon_authority | **PASS** | YES | NO | PASS |
| firestore_mirror | **PASS** | YES | NO | PASS |
| api_parity | **PASS** | YES | NO | PASS |
| dashboard_runtime | **PASS** | YES | NO | PASS |
| websocket_runtime | **NOT_APPLICABLE** | YES | NO | WebSocket requires authentication. |
| failure_injection | **PASS** | YES | NO | PASS |
| security | **PASS** | YES | NO | PASS |
| audit_reconciliation | **PASS** | YES | NO | PASS |
