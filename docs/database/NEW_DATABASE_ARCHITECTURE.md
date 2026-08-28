# NEW DATABASE ARCHITECTURE (RC-4 Hybrid)

## 🏗️ Hybrid Topology

```mermaid
graph TD
    API[FastAPI Gateway] --> Repo[Repository Abstraction Layer]
    
    subgraph "Operational Tier (PostgreSQL)"
        Repo --> PG[Operational DB]
        PG --> Stocks[Stocks & Prices]
        PG --> Intel[Regimes & News]
        PG --> Pred[Predictions & Models]
    end
    
    subgraph "Analytical Tier (DuckDB + Parquet)"
        Repo --> Duck[DuckDB Engine]
        Duck --> Features[Feature Store]
        Duck --> Training[ML Datasets]
        Duck --> Audit[Strategy Backtests]
    end
    
    subgraph "User Tier (Firestore)"
        Repo --> FS[Cloud Firestore]
        FS --> Users[Auth & Profile]
        FS --> Watch[Watchlists]
        FS --> Notes[Research Notes]
        FS --> Journal[Trade Journal]
    end
    
    subgraph "Cache Tier (Upstash Redis)"
        Repo --> Redis[Redis Cache]
        Redis --> Dashboard[Aggregated Stats]
        Redis --> Session[User Context]
    end
```

## 📊 Data Mapping Summary

| Technology | Purpose | Primary Data Types |
| :--- | :--- | :--- |
| **PostgreSQL** | Operational / Relational | Market Metadata, Tickers, Live Predictions, Audit Logs. |
| **DuckDB** | Analytical / Batch | Feature Vectors, Historical OHLC (Analytical), Training Buffers. |
| **Firestore** | User / Real-time | Profiles, Watchlists, Research Notes, Terminal Layouts. |
| **Redis** | Speed / Cache | Top Lists, Sector Heatmaps, Session Context. |

## ⚙️ Repository Layer Abstraction
The `IRepository` interfaces remain unchanged. The implementation will now manage multi-source data retrieval:
- `StockRepository` fetches metadata from **Postgres** but user watchlists from **Firestore**.
- `DataPlatformRepository` ingests news into **Postgres** but saves large training blobs into **Parquet** files queryable by **DuckDB**.
