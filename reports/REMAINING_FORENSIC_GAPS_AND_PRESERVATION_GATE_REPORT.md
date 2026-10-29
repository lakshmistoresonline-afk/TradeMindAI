# TradeMindAI R4.6.40 — Forensic Integrity Gate Audit & Remediated Ingestion Report

## 1. Executive Status & Gate Verdict Matrix

**Overall Preservation Gate Verdict**: **`PARTIAL`** (499/500 Equities Verified Complete; 1 Unlisted Equity `BAGMANE` Unresolved)  
**Production Acceptance Status**: **`BLOCKED`** (Preservation Hold Active; Phase 1 TejHQ Integration Blocked)  
**Gate A (INOXWIND Transaction Audit)**: **`RECONCILED`** (DuckDB & Parquet contain 2,853 matching rows under `TX_a1d391b2e9db`; unlinked stale staged path cleaned)  
**Gate B (Persisted Store Integrity)**: **`PASS`** (0 OHLC geometry violations, 0 non-positive prices, 0 duplicate keys, 0 NaN/Inf values across 1,143,549 rows; 499 DuckDB symbols == 499 Parquet files, 0 value mismatches at <1e-4 tolerance)  
**Gate C (BAGMANE Universe Validity)**: **`UNVERIFIED`** (`BAGMANE` is an unlisted private real estate developer in India with no active public exchange listing or Yahoo Finance ticker)  
**Gate D (Historical Coverage Audit)**: **`PARTIAL`** (306 full 10-year 2015-2026 equities + 193 post-2015 listed equities = 499 verified equities)  
**Gate E (Signal Engine Validation)**: **`PASS`** (Zero-lookahead Donchian breakout; dynamic `conviction_score` in [50, 95]; conservative same-bar stop-loss-first handling; 97,440 trade evaluations across 5, 10, 20, 60 session horizons)  
**Safety Invariants Status**: **`VERIFIED ENFORCED`** (`QUARANTINE_ACTIVE = true`, `REAL_TRADING = false`, `LIVE_EXECUTION_ENABLED = false`, `BROKER_ORDER_EXECUTION_ENABLED = false`)

---

## 2. Gate A — Forensic INOXWIND Transaction Audit Findings

- **DuckDB `daily_ohlcv` Store**: **2,853 rows** (2015-04-09 through 2026-10-27) committed under transaction tag `TX_a1d391b2e9db`.
- **Parquet Store (`INOXWIND.parquet`)**: **2,853 rows** (2015-04-09 through 2026-10-27).
- **DuckDB-to-Parquet Store Alignment**: **100% exact match** in row count, date sets, and OHLCV values.
- **Journal & Staged Path Resolution**: Journal entry `tx_id: 12adf270c32e` was created during a subsequent retry attempt that was interrupted before DuckDB commit. Stale staged path `tmplsiovqeq.parquet` was unlinked during cleanup. Checkpoint reflects `SUCCESS` with 2,853 rows.

---

## 3. Gate B — Complete Persisted-Store Audit Results

Audit performed read-only across all **1,143,549 live DuckDB records** and **499 Parquet feature store files**:

| Quality Audit Metric | DuckDB Store Outcome | Parquet Store Outcome | Alignment Status |
|---|---|---|---|
| **Total Cumulative Rows** | 1,143,549 rows | 1,143,549 rows | **100% EXACT MATCH** |
| **Distinct Symbol Count** | 499 symbols | 499 `.parquet` files | **100% EXACT MATCH** |
| **OHLC Geometry Violations** | 0 Violations | 0 Violations | **PASS** |
| **Price / Volume Violations** | 0 Non-positive prices | 0 Non-positive prices | **PASS** |
| **Duplicate (Symbol, Date) PKs** | 0 Duplicate Keys | 0 Duplicate Dates | **PASS** |
| **Numeric Integrity (NaN / Inf)** | 0 NaN/Inf | 0 NaN/Inf | **PASS** |
| **Store Value Equality (<1e-4 tol)** | 499 symbols matched | 499 symbols matched | **0 MISMATCHES** |

---

## 4. Gate C & D — Universe & Historical Coverage Audit Results

- **Canonical Nifty 500 Universe**: 500 Equities (`backend/app/db/nifty500_symbols.py`).
- **Full 10-Year History Equities (2015–2026)**: **306 Equities**
- **Post-2015 Listed Equities**: **193 Equities** (e.g. `ATGL` with 1,968 rows, `LICI` with 1,098 rows, `NYKAA`, `PAYTM`)
- **Unverified / Unlisted Equities**: **1 Equity (`BAGMANE`)** - Bagmane Developers Ltd., a private real estate developer entity in India with no active public exchange listing or Yahoo Finance ticker (`BAGMANE.NS`).
- **Total Ingested & Verified Equities**: **499 / 500 Equities (99.8% universe coverage)**.

---

## 5. Gate E — Remediated Multi-Horizon Walk-Forward Signal Performance

### A. Candidate & Evaluation Accounting
- **Total Scanned Price Bars**: **1,143,549 bars** across 499 symbols.
- **Total Candidate BUY Setups**: **24,369 setups**.
- **Active Current Setups (Near Present 2026-10-27)**: **9 setups** (no future bars available to evaluate).
- **Total Evaluated Trades per Horizon**: $24,369 - 9 = \mathbf{24,360\text{ trades per horizon}}$ ($24,360 \times 4 = \mathbf{97,440\text{ total trade evaluations}}$ across 4 horizons).

### B. Out-of-Sample Performance by Prediction Horizon

| Prediction Horizon | Total Evaluated Trades | Target Hits (+8.0%) | Stop Losses (-5.0%) | Expired Trades | Win Rate (%) | Avg Trade PnL (%) |
|---|---|---|---|---|---|---|
| **5 Sessions** | 24,360 | 4,214 | 6,376 | 13,770 | **17.30%** | **+0.43%** |
| **10 Sessions** | 24,360 | 6,576 | 9,459 | 8,325 | **27.00%** | **+0.58%** |
| **20 Sessions** | 24,360 | 8,971 | 11,906 | 3,483 | **36.83%** | **+0.69%** |
| **60 Sessions** | 24,360 | 10,679 | 13,407 | 274 | **43.84%** | **+0.77%** |

---

## 6. Safety Invariants & Unit Test Suite Output

- `REAL_TRADING = false` (Runtime value: `False`)
- `LIVE_EXECUTION_ENABLED = false` (Runtime value: `False`)
- `BROKER_ORDER_EXECUTION_ENABLED = false` (Runtime value: `False`)
- `QUARANTINE_ACTIVE = true` (Runtime value: `True`)
- **Unit Test Suite Output**: **58 PASSED / 0 FAILED** (`test_operational_api.py`, `test_quarantine_enforcement.py`, `test_ingestion_pipeline.py`)

Deliverable report saved at:
- [REMAINING_FORENSIC_GAPS_AND_PRESERVATION_GATE_REPORT.md](file:///D:/TradeMindAI/reports/REMAINING_FORENSIC_GAPS_AND_PRESERVATION_GATE_REPORT.md)
