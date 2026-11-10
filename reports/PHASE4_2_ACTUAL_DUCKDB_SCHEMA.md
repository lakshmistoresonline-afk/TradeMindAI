# Phase 4.2 Discovered DuckDB Schemas & Parquet Inventory Report

**Date**: 2026-11-03  
**Database File**: `backend/data/analytical.duckdb`  
**Features Directory**: `backend/data/features` (1,994 Parquet Files)

## 1. Discovered DuckDB Schemas

### `daily_ohlcv` Table Schema
```sql
CREATE TABLE daily_ohlcv (
    symbol VARCHAR NOT NULL PRIMARY KEY,
    date VARCHAR NOT NULL PRIMARY KEY,
    open DOUBLE,
    high DOUBLE,
    low DOUBLE,
    close DOUBLE,
    volume DOUBLE,
    source VARCHAR,
    ingested_at VARCHAR
);
```

### `intraday_5m_ohlcv` Table Schema
```sql
CREATE TABLE intraday_5m_ohlcv (
    symbol VARCHAR NOT NULL PRIMARY KEY,
    timestamp VARCHAR NOT NULL PRIMARY KEY,
    open DOUBLE,
    high DOUBLE,
    low DOUBLE,
    close DOUBLE,
    volume DOUBLE,
    source VARCHAR,
    ingested_at VARCHAR
);
```

## 2. Parquet Storage Content Inspection
- **Total Parquet Files Content-Inspected**: 1,994 files
- **Inventory File Generated**: [reports/PHASE4_2_PARQUET_CONTENT_INVENTORY.csv](file:///D:/TradeMindAI/reports/PHASE4_2_PARQUET_CONTENT_INVENTORY.csv)
