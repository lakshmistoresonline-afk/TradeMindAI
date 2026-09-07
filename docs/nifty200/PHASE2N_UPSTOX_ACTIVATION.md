# PHASE 2N: UPSTOX ACTIVATION STATUS

## 1. Objective
Activate the Upstox V3 Market Data Feed for production shadow monitoring.

## 2. Status
- **Authentication**: **PENDING**
- **Connectivity**: **OFFLINE**
- **Token Type**: Analytics Token (Long-lived)

## 3. Configuration Requirements
To activate this provider, the following environment variable must be populated in the production environment:
- `UPSTOX_ANALYTICS_TOKEN`

## 4. Activation Blockers
- **Authentication Required**: No valid analytics token found in the current `.env` environment.
- **Symbol Key Mapping**: The `UpstoxProvider` requires an active instrument master lookup to map internal IDs to `NSE_FO|...` keys.

---
**Status**: AUTHENTICATION_REQUIRED
