# TRADEMIND AI: PHASE 2U — PROVIDER-SCOPED SCORECARD

TIMESTAMP: 2026-09-08T10:41:09.590505

## 1. Global Gates
| Gate | Status | Blocking | Reason |
| :--- | :--- | :--- | :--- |
| population_integrity | **PASS** | NO | PASS |
| v22_freeze | **PASS** | NO | PASS |
| zero_fabrication | **PASS** | NO | PASS |
| failover_logic | **PASS** | NO | PASS |
| neon_authority | **PASS** | NO | PASS |
| api_parity | **PASS** | NO | PASS |
| dashboard_parity | **PASS** | NO | PASS |
| fno_derivative_pricing | **CONFIGURATION_REQUIRED** | YES | No authenticated F&O provider is currently available to supply genuine derivative prices. |

## 2. Angel One Scoped Audit
STATUS: **ANGELONE_ACTIVATION_PENDING**

| Gate | Status | Reason |
| :--- | :--- | :--- |
| implementation | **PASS** | PASS |
| configuration | **CONFIGURATION_REQUIRED** | ANGELONE_API_KEY, ANGELONE_CLIENT_CODE, ANGELONE_PIN and ANGELONE_TOTP_SECRET are absent from the production environment. |
| authentication | **CONFIGURATION_REQUIRED** | Authentication was not attempted because required Angel One production credentials are absent. |
| instrument_master | **CONFIGURATION_REQUIRED** | Angel One instrument-master synchronization has not occurred because an authenticated Angel One session is required. |
| equity_live | **DATA_UNAVAILABLE** | No genuine Angel One equity quote was retrieved because Angel One authentication is unavailable. |
| fno_live | **DATA_UNAVAILABLE** | No genuine Angel One derivative quote was retrieved because Angel One authentication is unavailable. |

## 3. Historical Scoped Audits (Reference)
UPSTOX STATUS: **UPSTOX_ACTIVATION_PENDING**
DHAN STATUS:   **DHAN_ACTIVATION_PENDING**
