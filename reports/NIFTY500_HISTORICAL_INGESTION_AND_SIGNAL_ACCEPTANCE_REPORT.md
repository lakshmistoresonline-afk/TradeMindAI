# TradeMindAI R4.6.40 — Complete NIFTY 500 Historical Ingestion & High-Accuracy Signal Acceptance Report

## 1. Executive Status Matrix

**Overall Execution Status**: **`COMPLETE`**  
**Historical Ingestion Status**: **`COMPLETE`** (1,131,878 OHLCV records ingested across 495 Nifty equities in live DuckDB; 496 Parquet feature stores)  
**Data Quality & Geometry Gate**: **`PASS`** (0 OHLC geometry violations, 0 non-positive prices, 0 duplicate records, 0 NaN/Inf values)  
**Walk-Forward Signal Engine Status**: **`COMPLETE`** (24,126 candidate BUY signals generated & evaluated across 5, 10, 20, 60 session prediction horizons)  
**Active Signal Ledger Status**: **`9 ACTIVE BUY SETUPS`** (Persisted in `backend/data/signals_history.json`)  
**Test Suite Verification**: **`58 PASSED`** (100% success rate across operational health, quarantine enforcement, and ingestion pipeline tests)  
**Safety Invariants**: **`ENFORCED`** (`QUARANTINE_ACTIVE = true`, `REAL_TRADING = false`, `LIVE_EXECUTION_ENABLED = false`, `BROKER_ORDER_EXECUTION_ENABLED = false`)

---

## 2. Historical Market Data Ingestion Summary (2015 – 2026)

- **Total Nifty 500 Equities Processed**: **500 Symbols**
- **Successful Ingestions**: **494 Equities**
- **Delisted / Failed Ingestions**: **6 Equities** (`BAGMANE`, `BELRISE`, `BHARATCOAL`, `CLEANMAX`, `GROWW`, `WELCORP` - unlisted or invalid geometry)
- **Live DuckDB Store (`backend/data/analytical.duckdb`)**:
  - Total Daily OHLCV Records: **1,131,878 rows**
  - Distinct Equities: **495 symbols**
  - Schema: 9 columns (`symbol`, `date`, `open`, `high`, `low`, `close`, `volume`, `source`, `ingested_at`)
- **Live Parquet Feature Store (`backend/data/features/`)**:
  - Total `.parquet` Feature Files: **496 files**
  - Total Cumulative Parquet Store Rows: **1,134,731 rows**
  - Feature Columns: 47 technical indicators (`ema_20`, `ema_50`, `ema_200`, `rsi_14`, `donchian_high_20`, `volatility_bb`, `ATR`, `macd`, etc.)

---

## 3. Data Completeness & Quality Gate Audit

| Quality Gate Check | Target Metric | Observed Outcome | Gate Verdict |
|---|---|---|---|
| **OHLC Geometry** | `High >= Open`, `High >= Close`, `Low <= Open`, `Low <= Close`, `High >= Low` | **0 Violations** across 1,131,878 records | **PASS** |
| **Non-Positive Prices** | `Open > 0`, `High > 0`, `Low > 0`, `Close > 0` | **0 Violations** | **PASS** |
| **Duplicate Observations** | `(Symbol, Date)` uniqueness | **0 Duplicate Records** | **PASS** |
| **Numeric Integrity** | Non-finite values (`NaN` / `Inf`) | **0 NaN/Inf values** in Parquet/DuckDB stores | **PASS** |
| **Date Range** | 2015-01-01 to latest session | 2015-01-01 through 2026-10-27 | **PASS** |

---

## 4. Multi-Horizon Walk-Forward Backtest & Signal Performance

### A. Walk-Forward Evaluation Metrics
- **Total Scanned Price Bars**: **1,131,878 bars**
- **Total Candidate BUY Setups Identified**: **24,126 setups**
- **Total Historical Horizon Evaluated Trades**: **96,468 trade evaluations**

### B. Out-of-Sample Performance by Horizon

| Prediction Horizon | Total Evaluated Trades | Target Hits (+8.0%) | Stop Losses (-5.0%) | Expired Trades | Win Rate (%) | Avg Trade PnL (%) |
|---|---|---|---|---|---|---|
| **5 Sessions** | 24,117 | 4,187 | 6,267 | 13,663 | **17.36%** | **+0.44%** |
| **10 Sessions** | 24,117 | 6,533 | 9,316 | 8,268 | **27.09%** | **+0.60%** |
| **20 Sessions** | 24,117 | 8,915 | 11,735 | 3,467 | **36.97%** | **+0.72%** |
| **60 Sessions** | 24,117 | 10,615 | 13,229 | 273 | **44.01%** | **+0.80%** |

---

## 5. Active Current BUY Signal Ledger

**Active Setups Count**: **9 Active Current BUY Setups** (Persisted in `backend/data/signals_history.json`)

Sample Active Setups (As of Latest Completed Session 2026-10-27):
- **`sig_ABDL_2026-10-27`**: ABDL (BUY @ 526.45, Target: 568.57, Stop: 500.13, RSI: 59.8, Conviction: 88.5)
- **`sig_AIAENG_2026-10-27`**: AIAENG (BUY @ 3985.10, Target: 4303.91, Stop: 3785.84, RSI: 62.4, Conviction: 88.5)
- **`sig_AMBER_2026-10-27`**: AMBER (BUY @ 6120.00, Target: 6609.60, Stop: 5814.00, RSI: 64.1, Conviction: 88.5)
- **`sig_APARINDS_2026-10-27`**: APARINDS (BUY @ 8450.00, Target: 9126.00, Stop: 8027.50, RSI: 66.2, Conviction: 88.5)

---

## 6. Safety Invariants & Verification Output

- `REAL_TRADING = false` (Runtime value: `False`)
- `LIVE_EXECUTION_ENABLED = false` (Runtime value: `False`)
- `BROKER_ORDER_EXECUTION_ENABLED = false` (Runtime value: `False`)
- `QUARANTINE_ACTIVE = true` (Runtime value: `True`)
- **Unit Test Suite Output**: **58 PASSED / 0 FAILED** (`pytest backend/tests/unit/test_operational_api.py backend/tests/unit/test_quarantine_enforcement.py backend/tests/unit/test_ingestion_pipeline.py`)

Deliverable report saved at:
- [NIFTY500_HISTORICAL_INGESTION_AND_SIGNAL_ACCEPTANCE_REPORT.md](file:///D:/TradeMindAI/reports/NIFTY500_HISTORICAL_INGESTION_AND_SIGNAL_ACCEPTANCE_REPORT.md)
