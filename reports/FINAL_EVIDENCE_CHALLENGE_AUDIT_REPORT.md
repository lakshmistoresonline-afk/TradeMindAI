# TradeMindAI R4.6.40 — Final Evidence Challenge & Read-Only Audit Report

## 1. Executive Status & Gate Verdict Matrix

**Overall Production Acceptance Status**: **`BLOCKED`** (Preservation Hold Active; Phase 1 TejHQ Integration Blocked)  
**Gate A (`INOXWIND` Transaction Lifecycle)**: **`PARTIAL / UNVERIFIED`** (DuckDB & Parquet contain 2,853 matching rows under `TX_a1d391b2e9db`; failed retry attempt `12adf270c32e` download interruption lifecycle unverified from logs alone)  
**Gate B (Persisted Store Integrity)**: **`PASS (TOLERANCE MATCH < 1e-4)`** (0 invalid/Null/NaN/Inf cells, 0 OHLC geometry violation rows, 0 duplicate keys, 0 non-positive price rows across 1,143,549 rows; 499 DuckDB symbols == 499 Parquet files, 0 value mismatches at <1e-4 numeric tolerance)  
**Gate C (Nifty 500 Universe Provenance & `BAGMANE`)**: **`UNVERIFIED`** (`BAGMANE` is mapped to "Bagmane Developers Ltd." in local universe source; Yahoo Finance `BAGMANE.NS` returns no data; official local constituent records unavailable)  
**Gate D (Genuine Historical Coverage)**: **`PARTIAL / UNVERIFIED`** (306 10-year 2015-2026 equities + 193 post-2015 listed equities = 499 verified equities; official exchange listing calendar files unavailable locally)  
**Gate E (Signal Engine Methodology & Accounting)**: **`PASS (METHODOLOGY & CODE INSPECTED)`** (Zero-lookahead Donchian breakout `shift(1)`; dynamic non-probabilistic `conviction_score` in [50, 95]; conservative same-bar stop-loss-first handling; 25,000 JSON array cap vs 97,440 total trade evaluations reconciled)  
**Safety Controls Enforcement Audit**: **`PASS (RUNTIME SETTINGS CHECK)`** (`QUARANTINE_ACTIVE = true`, `REAL_TRADING = false`, `LIVE_EXECUTION_ENABLED = false`, `BROKER_ORDER_EXECUTION_ENABLED = false`. *Qualification*: Runtime settings verification: PASS — the settings object returned the required values during this check. This result does not independently prove enforcement across every execution pathway.)

---

## 2. Gate A — INOXWIND Transaction Lifecycle Findings

- **Confirmed Fact (`TX_a1d391b2e9db`)**: Executed and committed on `2026-10-28T11:30:57`. DuckDB `daily_ohlcv` table contains **2,853 rows** committed under source tag `TX_a1d391b2e9db`. `INOXWIND.parquet` contains **2,853 matching rows** (2015-04-09 through 2026-10-27). Checkpoint records `status = SUCCESS` with 2,853 rows.
- **Confirmed Fact (`12adf270c32e`)**: Created during a subsequent re-ingestion attempt on `2026-10-28T11:41:51` that failed during download (`status: FAILED`). Zero rows exist in DuckDB with tag `TX_12adf270c32e`.
- **Unverified Inference**: The exact network error that interrupted `12adf270c32e` cannot be proven without external process logs.
- **Verdict**: **`PARTIAL / UNVERIFIED`**.

---

## 3. Gate B — Complete Persisted-Store Audit Results

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
| **DuckDB vs Parquet Value Mismatches (<1e-4)** | 499 symbols matched | 499 symbols matched | **TOLERANCE MATCH (< 1e-4)** |

---

## 4. Gate C & D — Universe Provenance & Historical Coverage Audit Results

- **Canonical Nifty 500 Universe**: 500 Equities (`backend/app/db/nifty500_symbols.py`).
- **Full 10-Year History Equities (2015–2026)**: **306 Equities**
- **Post-2015 Listed Equities**: **193 Equities** (e.g. `ATGL` with 1,968 rows, `LICI` with 1,098 rows, `NYKAA`, `PAYTM`)
- **Unverified / Unlisted Equities**: **1 Equity (`BAGMANE`)** - Bagmane Developers Ltd., mapped in local universe source; Yahoo Finance ticker `BAGMANE.NS` returns no data.
- **Total Ingested Equities**: **499 / 500 Equities (99.8% universe coverage)**.
- **Gate C Verdict**: **`UNVERIFIED`** (`BAGMANE` status unverified without local official constituent transition records).
- **Gate D Verdict**: **`PARTIAL / UNVERIFIED`** (Post-2015 start dates are observed start dates; official exchange listing calendar files unavailable locally).

---

## 5. Gate E — Signal Engine Validation & Accounting Reconciliation

### A. Candidate & Evaluation Accounting
- **Total Scanned Price Bars**: **1,143,549 bars** across 499 symbols.
- **Total Candidate BUY Setups**: **24,369 setups**.
- **Active Current Setups (Near Present 2026-10-27)**: **9 setups** (no future bars available to evaluate).
- **Total Evaluated Trades per Horizon**: $24,369 - 9 = \mathbf{24,360\text{ trades per horizon}}$ ($24,360 \times 4 = \mathbf{97,440\text{ total trade evaluations}}$ across 4 horizons).
- **25,000 Persisted JSON Cap Reconciliation**: The payload caps `history_records` at 25,000 items (`all_history_signals[:25000]`) to constrain file size on disk, while `summary["total_evaluations"]` retains the true 97,440 count.

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
- **Files Created/Modified During Earlier Audit Runs**:
  - Audit Scripts: `scripts/audit/gate_a_inoxwind_lifecycle_trace.py`, `scripts/audit/gate_b_comprehensive_store_audit.py`, `scripts/audit/gate_cd_universe_and_coverage.py`, `scripts/audit/gate_e_signal_and_safety_audit.py`, `scripts/audit/gate_a_inoxwind_lifecycle_trace.py`, `scripts/audit/gate_b_comprehensive_store_audit.py`, `scripts/audit/gate_cd_universe_and_coverage.py`.
  - Deliverable Reports: `reports/FORENSIC_GATE_CORRECTION_AND_EA_AUDIT_REPORT.md`, `reports/FINAL_EVIDENCE_CHALLENGE_AUDIT_REPORT.md`.
- **Formatting Verification (`git diff --check`)**: **PASS** (Exit Code: `0`, zero formatting errors).
- **Release Decision**: **`BLOCKED`** (Preservation Hold Active). TejHQ data provider integration (Phase 1) remains blocked.

Deliverable report saved at:
- [FINAL_EVIDENCE_CHALLENGE_AUDIT_REPORT.md](file:///D:/TradeMindAI/reports/FINAL_EVIDENCE_CHALLENGE_AUDIT_REPORT.md)
- [FORENSIC_GATE_CORRECTION_AND_EA_AUDIT_REPORT.md](file:///D:/TradeMindAI/reports/FORENSIC_GATE_CORRECTION_AND_EA_AUDIT_REPORT.md)
- [REMAINING_FORENSIC_GAPS_AND_PRESERVATION_GATE_REPORT.md](file:///D:/TradeMindAI/reports/REMAINING_FORENSIC_GAPS_AND_PRESERVATION_GATE_REPORT.md)
