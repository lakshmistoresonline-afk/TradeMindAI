# TradeMind Open Market Data Fabric (Architecture)

## 1. Overview
The **TradeMind Open Market Data Fabric** is a ₹0-cost, institutional-grade market data infrastructure designed to provide reliable NIFTY-200 Equity and F&O data using only public and open-source sources.

## 2. Components

### A. Local Open Data Collector (Windows Gateway)
- **Role**: Standalone collector running on local Windows infrastructure.
- **Responsibility**: Fetching data from public NSE endpoints (`nseindia.com`) to bypass cloud IP blocks.
- **Transport**: Pushes validated market snapshots to the Railway backend via authenticated HTTPS.
- **Cache**: Implements local session management and request deduplication.

### B. backend/infrastructure/repositories/nse_open_provider.py
- **Role**: Backend provider adapter integrated into the `PriceResolver`.
- **Strategy**: 
    1. Reads latest ingested data from Neon (Primary).
    2. Optional direct fetch from public APIs if running in an unblocked environment (Secondary).

### C. backend/api/v1/endpoints/market_data.py
- **Role**: Ingestion gateway for the local collector.
- **Security**: X-Collector-Key authentication enforced.

## 3. Data Flow
1. **Collector** (Local PC) -> Fetch public NSE data.
2. **Collector** -> Validate schema and quality.
3. **Collector** -> POST to `/api/v1/market-data/ingest`.
4. **Backend** -> Update `stocks` and `shadow_signals` in **Neon**.
5. **PriceResolver** -> Delivers verified price to **SignalEngine**.
6. **API/Dashboard** -> Presents truthful data to the user.

## 4. Hierarchy (Failover)
- **EQUITY**: NSE_OPEN -> AngelOne -> Upstox -> Dhan -> Groww -> YFinance.
- **F&O**: NSE_OPEN -> AngelOne -> Upstox -> Dhan -> Groww -> DATA_UNAVAILABLE.

---
**Status**: V1.0.0 IMPLEMENTED.
