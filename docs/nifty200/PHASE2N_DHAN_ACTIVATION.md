# PHASE 2N: DHANHQ ACTIVATION STATUS

## 1. Objective
Activate the DhanHQ Market Feed for forensic historical audits and F&O failover.

## 2. Status
- **Authentication**: **PENDING**
- **Connectivity**: **OFFLINE**

## 3. Configuration Requirements
To activate this provider, the following environment variables must be populated:
- `DHAN_ACCESS_TOKEN`
- `DHAN_CLIENT_ID`

## 4. Activation Blockers
- **Authentication Required**: Missing access token in the current configuration.
- **Instrument Master**: The `DhanProvider` requires a numerical `SecurityId` for all F&O requests, necessitating a daily-synced local instrument CSV.

---
**Status**: AUTHENTICATION_REQUIRED
