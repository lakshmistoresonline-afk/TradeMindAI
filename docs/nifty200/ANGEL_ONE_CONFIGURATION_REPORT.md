# ANGEL ONE SMARTAPI CONFIGURATION DISCOVERY REPORT

## 1. Environment & Deployment Summary

| Field | Value | Source | Confidence |
| :--- | :--- | :--- | :--- |
| **Backend Deployment Platform** | Railway | `railway.json` schema URL | HIGH |
| **Backend Public HTTPS Base URL** | `https://trademind-api-production.up.railway.app` | `web/src/api/client.ts` | HIGH |
| **Backend API URL** | `https://trademind-api-production.up.railway.app/api/v1` | `web/src/api/client.ts` | HIGH |
| **Firebase Frontend URL** | `https://com-webcraft-trademindai-c8f75.web.app` | `web/src/api/client.ts` | HIGH |
| **Backend Outbound IPv4** | UNKNOWN — REQUIRES CONFIGURATION | Runtime environment | N/A |
| **Static IPv4 Support** | YES (Via Railway Static Outbound IP Add-on) | Railway Platform Docs | HIGH |
| **Current Static IPv4 Status** | Likely NO | `railway.json` (no static IP config found) | MEDIUM |

## 2. Integration & Connectivity

| Field | Value | Source | Confidence |
| :--- | :--- | :--- | :--- |
| **Existing Auth Routes** | `/api/v1/auth/login`, `/api/v1/auth/register` | `backend/api/v1/endpoints/auth.py` | HIGH |
| **Angel One Callback URL** | UNKNOWN — REQUIRES CONFIGURATION | Codebase audit | HIGH |
| **New Callback Endpoint Needed** | YES (e.g., `/api/v1/auth/angelone/callback`) | Codebase audit | HIGH |
| **Existing Angel One Integration**| NONE | Codebase audit | HIGH |
| **Market Data Standalone Support**| YES (via Market Feeds API Key) | Official SmartAPI Documentation | HIGH |

## 3. Provider Infrastructure

| Field | Value | Source | Confidence |
| :--- | :--- | :--- | :--- |
| **Existing Adapter Names** | `UpstoxProvider`, `DhanProvider`, `GrowwProvider`, `YFinanceProvider` | `backend/infrastructure/repositories/` | HIGH |
| **Upstox Configuration** | `UPSTOX_ANALYTICS_TOKEN` | `upstox_provider.py` | HIGH |
| **Dhan Configuration** | `DHAN_ACCESS_TOKEN`, `DHAN_CLIENT_ID` | `dhan_provider.py` | HIGH |
| **Angel One Env Variables** | UNKNOWN — REQUIRES CONFIGURATION | `.env` audit | HIGH |

## 4. Safety & Strategy Status

| Field | Value | Source | Confidence |
| :--- | :--- | :--- | :--- |
| **REAL_TRADING** | **FALSE** | `certification_engine_v2t.py` | HIGH |
| **BROKER_ORDER_ENABLED** | **FALSE** | System Rules & Design | HIGH |
| **Strategy V2.2 Status** | **FROZEN** | System Rules | HIGH |

---
**Verdict**: The infrastructure is ready for a new provider adapter. Deployment on Railway supports static outbound IPs if required for high-tier API access, but standard Market Feeds can be accessed via dynamic IPs using TOTP authentication. No existing Angel One logic or credentials were discovered.
