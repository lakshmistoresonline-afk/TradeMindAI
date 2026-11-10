# TradeMindAI — Phase E Historical Data Provenance Report

**Audit Scope**: Historical market data providers, stored Parquet/DuckDB datasets, date ranges, timeframe resolutions, price adjustment policies, timezones, and data quality status.  
**Repository**: `D:\TradeMindAI`  
**Phase Verdict**: **`PHASE E BLOCKED`** (Backtesting reliability and data provenance verified; protected file fallbacks blocked pending authorization)

---

## 1. Stored Dataset Provenance Inventory

| Dataset Tier | Storage Location | Symbol Scope | Date Range | Timeframe | Adjustment Policy | Timezone | Data Quality Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: |
| **Analytical DuckDB** | `backend/data/analytical.duckdb` | 500 NIFTY 500 Equities | `2015-01-01` to as-of date | `1D` & `5M` | `auto_adjust = True` | `Asia/Kolkata` | **PASS** |
| **Daily Parquet** | `backend/data/features/{symbol}.parquet` | 500 NIFTY 500 Equities | `2015-01-01` to as-of date | `1D` | `auto_adjust = True` | `Asia/Kolkata` | **PASS** |
| **Intraday Parquet** | `backend/data/features/{symbol}_5m.parquet` | 500 NIFTY 500 Equities | Completed trading sessions | `5M` | `auto_adjust = True` | `Asia/Kolkata` | **PASS** |

---

## 2. Incomplete Active Session Guard

Function `HistoricalBackfillService.validate_historical_bar()` enforces strict as-of date boundaries (`bar_date <= as_of_completed_date`). Active incomplete daily candles during market trading hours are filtered out to prevent partial bar pollution in historical daily dataset storage.
