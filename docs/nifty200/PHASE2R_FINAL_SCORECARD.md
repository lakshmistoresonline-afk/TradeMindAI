# TRADEMIND AI: PHASE 2R — FINAL INSTITUTIONAL SCORECARD

| Gate | Status | Mandatory | Blocking | Reason |
| :--- | :--- | :--- | :--- | :--- |
| population_integrity | **PASS** | YES | NO | PASS |
| v22_freeze | **PASS** | YES | NO | PASS |
| instrument_master | **FAIL** | YES | YES | No instruments found in Neon for provider Upstox. Sync required. |
| upstox_authentication | **CONFIGURATION_REQUIRED** | YES | YES | Analytics Token missing. |
| dhan_authentication | **CONFIGURATION_REQUIRED** | YES | YES | Access Token missing. |
| provider_activation | **CONFIGURATION_REQUIRED** | YES | YES | All F&O providers require production credentials. |
| fno_identity | **PASS** | YES | NO | PASS |
| fno_quote_retrieval | **CONFIGURATION_REQUIRED** | YES | YES | Live premiums blocked by missing authentication. |
| fno_derivative_pricing | **CONFIGURATION_REQUIRED** | YES | YES | Live premiums blocked by missing authentication. |
| price_freshness | **DATA_UNAVAILABLE** | YES | YES | Truthful forensic reason required. |
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
