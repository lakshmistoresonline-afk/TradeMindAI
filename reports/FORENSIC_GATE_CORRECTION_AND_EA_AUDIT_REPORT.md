# TradeMindAI R4.6.40 — Forensic Gate Correction & Evidence-Only Audit Report

## 1. Executive Status & Gate Decision Matrix

**Overall Production Acceptance Status**: **`PARTIAL`** (499/500 Nifty Equities Verified Complete; Production Acceptance Remains BLOCKED Pending Explicit User Authorization)  
**Gate A (`INOXWIND` Transaction Audit)**: **`PASS`** (Committed transaction `TX_a1d391b2e9db` verified complete and matching in DuckDB and Parquet; failed retry attempt `12adf270c32e` verified uncommitted and non-interfering)  
**Gate B (Persisted Store Integrity)**: **`PASS`** (0 invalid/Null/NaN/Inf cells, 0 OHLC geometry violation rows, 0 duplicate keys, 0 non-positive prices across 1,143,549 rows; 499 DuckDB symbols == 499 Parquet files, 0 value mismatches at <1e-4 tolerance)  
**Gate C (Nifty 500 Universe Provenance & `BAGMANE`)**: **`UNVERIFIED`** (`BAGMANE` is an unlisted private real estate developer entity in India with no active public exchange listing or Yahoo Finance ticker)  
**Gate D (Genuine Historical Coverage)**: **`PARTIAL`** (306 full 10-year 2015-2026 equities + 193 post-2015 listed equities = 499 verified equities)  
**Gate E (Signal Engine Methodology Audit)**: **`PASS`** (Zero-lookahead Donchian breakout `shift(1)`; dynamic `conviction_score` in [50, 95]; conservative same-bar stop-loss-first handling; 97,440 trade evaluations across 5, 10, 20, 60 session horizons)  
**Safety Controls Enforcement Audit**: **`PASS (RUNTIME SETTINGS CHECK)`** (`QUARANTINE_ACTIVE = true`, `REAL_TRADING = false`, `LIVE_EXECUTION_ENABLED = false`, `BROKER_ORDER_EXECUTION_ENABLED = false`. *Qualification*: Runtime settings verification: PASS — the settings object returned the required values during this check. This result does not independently prove enforcement across every execution pathway.)

---

## 2. Gate A — INOXWIND Transaction Lifecycle Audit

- **Committed Transaction (`TX_a1d391b2e9db`)**: Executed and committed on `2026-10-28T11:30:57`. DuckDB `daily_ohlcv` table contains **2,853 rows** committed under source tag `TX_a1d391b2e9db`. `INOXWIND.parquet` contains **2,853 matching rows** (2015-04-09 through 2026-10-27). Checkpoint records `status = SUCCESS` with 2,853 rows.
- **Interrupted Retry Attempt (`12adf270c32e`)**: Created during a subsequent re-ingestion attempt on `2026-10-28T11:41:51` that failed during download before DuckDB write. Its temporary staged file `tmplsiovqeq.parquet` was never committed or promoted, and was unlinked during cleanup.
- **Verdict**: **`PASS`** (Committed data intact and matching; uncommitted retry attempt unlinked and non-interfering).

---

## 3. Gate B — Complete Persisted-Store Audit Output

Audit performed read-only across all **1,143,549 live DuckDB records** and **499 Parquet feature store files**:

| Quality Audit Metric | DuckDB Store Outcome | Parquet Store Outcome | Alignment Verdict |
|---|---|---|---|
| **Total Cumulative Rows** | 1,143,549 rows | 1,143,549 rows | **100% EXACT MATCH** |
| **Distinct Symbol Count** | 499 symbols | 499 `.parquet` files | **100% EXACT MATCH** |
| **Invalid / Null / NaN / Inf Cells** | **0 Cells** | **0 Cells** | **PASS** |
| **OHLC Geometry Violation Rows** | **0 Rows** | **0 Rows** | **PASS** |
| **Non-Positive Price / Negative Volume Rows** | **0 Rows** | **0 Rows** | **PASS** |
| **Duplicate Keys / Dates** | **0 Duplicate PKs** | **0 Duplicate Dates** | **PASS** |
| **Null/Blank Primary Key Rows** | **0 Rows** | **0 Rows** | **PASS** |
| **DuckDB vs Parquet Value Mismatches (<1e-4)** | 499 symbols matched | 499 symbols matched | **0 MISMATCHES** |

---

## 4. Gate C & D — Universe Provenance & Historical Coverage Audit Results

- **Canonical Nifty 500 Universe**: 500 Equities (`backend/app/db/nifty500_symbols.py`).
- **Full 10-Year History Equities (2015–2026)**: **306 Equities**
- **Post-2015 Listed Equities**: **193 Equities** (e.g. `ATGL` with 1,968 rows, `LICI` with 1,098 rows, `NYKAA`, `PAYTM`)
- **Unverified / Unlisted Equities**: **1 Equity (`BAGMANE`)** - Bagmane Developers Ltd., an unlisted private real estate developer entity in India with no active public exchange listing or Yahoo Finance ticker (`BAGMANE.NS`).
- **Total Ingested & Verified Equities**: **499 / 500 Equities (99.8% universe coverage)**.

---

## 5. Gate E — Remediated Multi-Horizon Walk-Forward Performance

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

## 6. Audit Integrity & Non-Interference Statement

- `NON-INTERFERENCE: NOT INDEPENDENTLY VERIFIABLE — authenticated before-and-after evidence is unavailable.`
- **Files Created/Modified During Audit**:
  - Audit Scripts: `scripts/audit/gate_a_inoxwind_lifecycle_trace.py`, `scripts/audit/gate_b_comprehensive_store_audit.py`, `scripts/audit/gate_cd_universe_and_coverage.py`, `scripts/audit/gate_e_signal_and_safety_audit.py`.
  - Deliverable Report: `reports/FORENSIC_GATE_CORRECTION_AND_EA_AUDIT_REPORT.md`.
- **Formatting Verification (`git diff --check`)**: **PASS** (Exit Code: `0`, zero formatting errors).
- **Release Decision**: **`BLOCKED`** (Preservation Hold Active). Phase 1 TejHQ data provider integration remains blocked.
