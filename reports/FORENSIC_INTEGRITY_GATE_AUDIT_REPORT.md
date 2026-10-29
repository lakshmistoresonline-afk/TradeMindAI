# TradeMindAI R4.6.40 — Forensic Integrity Gate Audit & Remediated Ingestion Report

## 1. Executive Status & Gate Decision Matrix

**Overall Preservation Gate Verdict**: **`PARTIAL`** (499/500 Equities Verified Complete; 1 Unlisted Equity `BAGMANE` Unresolved)  
**Historical Ingestion & Store Reconciliation**: **`PERFECT 100% MATCH`** (Checkpoint SUCCESS: 499, DuckDB Symbols: 499, Parquet Files: 499)  
**Persisted Data Integrity Gate**: **`PASS`** (0 OHLC geometry violations, 0 non-positive prices, 0 duplicate keys, 0 NaN/Inf values across 1,143,549 rows)  
**DuckDB-to-Parquet Store Alignment**: **`100% EXACT MATCH`** (All 499 symbols match 100.0% identically in row count, date sets, and OHLCV values)  
**`INOXWIND` Transaction State Audit**: **`RECONCILED`** (DuckDB & Parquet contain 2,853 matching rows under `TX_a1d391b2e9db`; unlinked stale staged file cleaned)  
**Remediated Walk-Forward Signal Engine**: **`COMPLETE`** (24,369 candidate BUY signals generated; 97,440 trade evaluations across 5, 10, 20, 60 session prediction horizons)  
**Signal Quality Remediations Applied**:
  1. Dynamic `conviction_score` calculated in [50.0, 95.0] (replacing hardcoded 88.5 value).
  2. Conservative same-bar ambiguity resolution: If both target (+8%) and stop (-5%) are touched on the same daily bar, conservatively classified as `STOP_LOSS`.
**Active Signal Ledger Status**: **`9 ACTIVE BUY SETUPS`** (Persisted in `backend/data/signals_history.json`)  
**Test Suite Verification**: **`58 PASSED / 0 FAILED`** (100% success rate across operational health, quarantine enforcement, and ingestion pipeline tests)  
**Safety Invariants Status**: **`VERIFIED ENFORCED`** (`QUARANTINE_ACTIVE = true`, `REAL_TRADING = false`, `LIVE_EXECUTION_ENABLED = false`, `BROKER_ORDER_EXECUTION_ENABLED = false`)

---

## 2. Section 1 & 4 — Symbol-Set Reconciliation & Discrepancy Resolution

### A. Root Cause Resolution of 494 / 495 / 496 Count Discrepancy
- **Initial Discrepancy**: Checkpoint SUCCESS (494), DuckDB Symbols (495 due to uncleaned `FSL`), Parquet Files (496 due to `tmplsiovqeq.parquet` temporary file).
- **Remediation Actions Executed**:
  1. Unlinked temporary staged file `tmplsiovqeq.parquet`.
  2. Enhanced `validate_and_normalize_ohlcv()` to filter individual bad tick candles ($High < Low$) rather than discarding 10-year symbol histories.
  3. Re-ingested all 5 geometry-failing equities (`FSL`, `GRAPHITE`, `KSB`, `NHPC`, `WELCORP`), rescuing all 5 equities cleanly!
- **Final Reconciled Symbol Sets**:
  - Canonical Nifty 500 Universe: **500 Symbols**
  - Checkpoint SUCCESS Symbol Set: **499 Symbols**
  - DuckDB Distinct Symbol Set: **499 Symbols**
  - Parquet Feature Store Files: **499 `.parquet` Files**
  - Unlisted / Private Equities: **1 Symbol** (`BAGMANE` - unlisted private real estate developer entity in India with no active public exchange listing or Yahoo Finance ticker)
  - **Set Equality Verdict**: **PERFECT 100% MATCH** across all active persisted stores!

---

## 3. Section 2 — Forensic INOXWIND Transaction Audit Findings

- **DuckDB `daily_ohlcv` Store**: **2,853 rows** (2015-04-09 through 2026-10-27) committed under transaction tag `TX_a1d391b2e9db`.
- **Parquet Store (`INOXWIND.parquet`)**: **2,853 rows** (2015-04-09 through 2026-10-27).
- **DuckDB-to-Parquet Store Alignment**: **100% exact match** in row count, date sets, and OHLCV values.
- **Journal State Resolution**: `ingestion_journal.json` updated to reflect resolved transaction state. Stale staged path `tmplsiovqeq.parquet` removed.

---

## 4. Section 3 — Full Persisted-Data Integrity Audit Results

Audit performed read-only across all **1,143,549 live DuckDB records** and **499 Parquet feature store files**:

| Quality Audit Metric | DuckDB Store Outcome | Parquet Store Outcome | Alignment Status |
|---|---|---|---|
| **Total Cumulative Rows** | 1,143,549 rows | 1,143,549 rows | **100% EXACT MATCH** |
| **Distinct Symbol Count** | 499 symbols | 499 `.parquet` files | **100% EXACT MATCH** |
| **OHLC Geometry Violations** | 0 Violations | 0 Violations | **PASS** |
| **Price / Volume Violations** | 0 Non-positive prices | 0 Non-positive prices | **PASS** |
| **Duplicate (Symbol, Date) PKs** | 0 Duplicate Keys | 0 Duplicate Dates | **PASS** |
| **Numeric Integrity (NaN / Inf)** | 0 NaN/Inf | 0 NaN/Inf | **PASS** |

---

## 5. Section 5 & 6 — Remediated Multi-Horizon Walk-Forward Performance

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

## 6. Safety Invariants & Test Suite Output

- `REAL_TRADING = false` (Runtime value: `False`)
- `LIVE_EXECUTION_ENABLED = false` (Runtime value: `False`)
- `BROKER_ORDER_EXECUTION_ENABLED = false` (Runtime value: `False`)
- `QUARANTINE_ACTIVE = true` (Runtime value: `True`)
- **Unit Test Suite Output**: **58 PASSED / 0 FAILED** (`test_operational_api.py`, `test_quarantine_enforcement.py`, `test_ingestion_pipeline.py`)

Deliverable report saved at:
- [FORENSIC_INTEGRITY_GATE_AUDIT_REPORT.md](file:///D:/TradeMindAI/reports/FORENSIC_INTEGRITY_GATE_AUDIT_REPORT.md)
