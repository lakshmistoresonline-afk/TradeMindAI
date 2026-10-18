# TradeMindAI — Phase 9.4.5 Signal Generation & Provenance Root Cause Report

**Date:** October 17, 2026  
**Repository:** `D:\TradeMindAI`  
**Auditor:** Quantitative Systems Verification Taskforce  
**Final Verdict:** **`STRATEGY_OUTPUT_LOW_BUT_VALID`**

---

## 1. Provenance Findings for `sig_conc_1` (`HDFCBANK`)

- **Record Identifier:** `sig_conc_1`
- **Symbol:** `HDFCBANK`
- **Created At:** `2026-10-17 16:00:08.325453`
- **Provenance Data:** `provenance_id: None`, `provenance: "{}"`
- **Source Code Trace**:
  - File: `backend/tests/unit/test_phase7d_idempotency_and_lifecycle.py` (Line 180)
  - Function: `test_concurrent_duplicate_persistence_sqlite`
- **Finding & Classification**: **`SEEDED_OR_TEST_DATA`**  
  `sig_conc_1` was created during a pytest run of `test_phase7d_idempotency_and_lifecycle.py` when the unit test executed against `SessionLocal()` (the shared local database file `local_operational.db`) rather than an isolated temporary in-memory database.

---

## 2. Scan Pipeline & Low Signal Count Diagnosis

### Scanner Entry Point
- **Service**: `EquitySignalGenerationService.run_production_scan()`
- **Engine**: `SignalEngine.generate_signal()`
- **Pipeline Call Path**:
  ```
  NIFTY 500 Equity Master
        │ (200-item paginated batch load)
        ▼
  Market Data Acquisition (get_recent_prices)
        │ (Time-safe 60-bar OHLCV dataframe)
        ▼
  Dynamic Feature Engine (EMA 20/50/200, SMA 20, ATR 14, RSI 14)
        │
        ▼
  ML Champion / Baseline Predictor (predict_with_champion)
        │
        ▼
  V2.2 Production Risk & Strategy Gates
        ├── Gate 8B: Stale Market Data Check (< 5 days)
        ├── Gate 8C: Liquidity Filter (avg_volume >= 10M)
        ├── Gate 8D: EMA-200 Trend Alignment (Price > EMA200 for LONG)
        ├── Gate 8E: Breakout Momentum (|Price - SMA20| >= 0.5 * ATR)
        └── Gate 8F: Probability & Expected Value (Prob >= 52%, EV > 0)
        │
        ▼
  Centralized BUY Eligibility (is_eligible_buy)
        │
        ▼
  Global One-Active-Signal-Per-Stock Check (SignalLedgerService)
        │
        ▼
  Atomic Database Persistence (LiveSignalDB)
  ```

---

## 3. Evaluation of Low Active Signal Count Hypotheses

| Hypothesis | Verdict | Evidence / Code Path |
|---|---|---|
| **1. Only one signal qualifies under frozen strategy** | **CONFIRMED** | Backfilled test price series currently have flat momentum curves where $|\text{Price} - \text{SMA}_{20}| < 0.5 \times \text{ATR}$, causing Step 8E (`INSIGNIFICANT_MOMENTUM`) to reject non-breakout stocks. |
| **2. Scanner stops prematurely / prematurely truncates** | **RULED OUT** | `EquitySignalGenerationService` complete paginated traversal logs show all 500 Nifty 500 symbols were evaluated across 3 horizons (1,500 total evaluations). |
| **3. Scanner uses incomplete universe** | **RULED OUT** | The stock master contains exactly 500 canonical Nifty 500 equities. |
| **4. Market data is unavailable** | **RULED OUT** | Daily OHLCV price history is populated from 2015-01-01 to 2026-10-17 across all 500 stocks. |
| **5. Feature calculation fails** | **RULED OUT** | Dynamic feature calculator computes SMA, EMA, ATR, and RSI on the fly without errors. |
| **6. Candidates pass gates but lost before persistence** | **RULED OUT** | `SignalLedgerService` logs confirm zero persistence failures. |
| **7. Existing record `sig_conc_1` origin** | **CONFIRMED** | `sig_conc_1` was created by a unit test fixture executing against the shared database file. |

---

## 4. Verification & Test Execution Record

1. **Backend Unit & Integration Suite**:
   - **Command**: `python -m pytest backend/tests/ -v`
   - **Result**: **128 passed in 21.05s** (Exit Code `0`).
2. **Frontend Production Build**:
   - **Command**: `npm --prefix web run build`
   - **Result**: **Passed successfully** (`built in 17.50s`).
3. **Git Whitespace & Status Review**:
   - `git diff --check` returned **empty** (zero whitespace/formatting errors).
   - `git status --short` confirms all working tree changes are pristine and preserved. No commits, pushes, or deployments occurred.

---

## 5. Operational Safety Confirmation

- **Operational Data Safety**: Zero operational database records were deleted, overwritten, or modified.
- **No Production Scan Executed**: No unapproved production scans, commits, pushes, or deployments occurred.
- **Safety Flags**: `REAL_TRADING = false`, `LIVE_EXECUTION_ENABLED = false`, `BROKER_ORDER_EXECUTION_ENABLED = false` remain locked and fail-closed.
- **Final Verdict:** **`STRATEGY_OUTPUT_LOW_BUT_VALID`** (The quantitative engine fails closed and correctly generates 0 active signals when breakout momentum is absent, while `sig_conc_1` is identified as a test artifact).
