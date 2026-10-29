# TradeMindAI R4.6.40 — Final Signal Methodology and Preservation Audit Report

## 1. Executive Status & Gate Verdict Matrix

**Overall Production Acceptance Status**: **`BLOCKED`** (Preservation Hold Active; Phase 1 TejHQ Integration Blocked)  
**Gate A (`INOXWIND` Transaction Lifecycle Audit)**: **`PARTIAL / UNVERIFIED`** (Committed transaction `TX_a1d391b2e9db` verified complete and matching in DuckDB and Parquet; failed retry attempt `12adf270c32e` download interruption lifecycle unverified without external process logs)  
**Gate B (Persisted Store Integrity)**: **`PASS (TOLERANCE MATCH < 1e-4)`** (0 invalid/Null/NaN/Inf cells, 0 OHLC geometry violation rows, 0 duplicate keys, 0 non-positive price rows across 1,143,549 rows; 499 DuckDB symbols == 499 Parquet files, 0 value mismatches at <1e-4 numeric tolerance)  
**Gate C (Nifty 500 Universe Provenance & `BAGMANE`)**: **`UNVERIFIED`** (`BAGMANE` is mapped to "Bagmane Developers Ltd." in local universe source; Yahoo Finance `BAGMANE.NS` returns no data; official local constituent transition records unavailable)  
**Gate D (Genuine Historical Coverage Audit)**: **`PARTIAL / UNVERIFIED`** (306 10-year 2015-2026 equities + 193 post-2015 listed equities = 499 verified equities; official exchange listing calendar files unavailable locally)  
**Gate E (Signal Engine Code Inspection & Accounting)**: **`PASS (CODE INSPECTED)`** (Zero-lookahead Donchian breakout `shift(1)`; dynamic non-probabilistic `conviction_score` in [50, 95]; conservative same-bar stop-loss-first handling; 25,000 JSON array cap vs 97,440 total trade evaluations reconciled)  
**Safety Controls Enforcement Audit**: **`PASS (RUNTIME SETTINGS CHECK)`** (`QUARANTINE_ACTIVE = true`, `REAL_TRADING = false`, `LIVE_EXECUTION_ENABLED = false`, `BROKER_ORDER_EXECUTION_ENABLED = false`. *Qualification*: Runtime settings verification: PASS — the settings object returned the required values during this check. This result does not independently prove enforcement across every execution pathway.)

---

## 2. Gate E — Detailed Implementation Code Audit Findings

Source Code Reference: [generate_walkforward_signals_duckdb.py](file:///D:/TradeMindAI/scripts/signals/generate_walkforward_signals_duckdb.py)

### A. Entry Timing and Fill Assumptions
- **Line 116**: `entry_dt = str(r["date"])`, `entry_p = float(r["Close"])`. Signal evaluation uses bar $i$'s closing price as `entry_price`.
- **Line 142**: Forward trade outcomes start at bar $i+1$ (`future_sub = df_sym.iloc[i+1 : i+1+horizon]`).
- **Fill Model Limitation**: Assuming entry occurs at the exact close price that generated the signal implies same-close execution or next-session open = bar $i$ close in daily models. In live markets, fill slippage between signal trigger and next-session open execution is expected.

### B. Indicator Correctness & Zero-Lookahead Enforcement
- **Line 109**: `donchian_high_20 = df_sym["High"].shift(1).rolling(window=20).max()`. Uses `shift(1)` to exclude current bar $i$ from Donchian high calculation, enforcing zero lookahead bias.
- **Lines 102–106**: RSI 14 calculation handles zero gain/loss via `gain / loss.replace(0, np.nan)` and `.fillna(50)`.
- **Lines 98–100**: Exponential Moving Averages (`ema_20`, `ema_50`, `ema_200`) use `.ewm(span=N, adjust=False).mean()`. The walk-forward loop requires a minimum history of 30 bars (`range(30, len(df_sym))`) before evaluating signals.

### C. Horizon Semantics and Trade Outcome Accounting
- **Line 142**: `future_sub = df_sym.iloc[i+1 : i+1+horizon]`. Slicing evaluates forward daily trading bars, so `horizon_days` represents **daily trading sessions**, not calendar days.
- **Line 161**: `if bar_high >= target_p and bar_low <= stop_p: status = "STOP_LOSS"`. Applies conservative same-bar stop-loss-first classification whenever both target (+8.0%) and stop (-5.0%) are touched on the same daily bar.
- **Incomplete Horizons**: For setups near the dataset end-date (2026-10-27), `future_sub` is empty (`iloc[i+1 : i+1+horizon]`). These 9 candidate setups are classified as active current setups (`status: ACTIVE`).

### D. Evaluation Count and 25,000 JSON Array Cap
- **Total Candidates Generated**: **24,369 setups** across 1,143,549 price bars.
- **Active Current Setups (Near Present 2026-10-27)**: **9 setups** (no future bars available to evaluate).
- **Evaluated Trades per Horizon**: $24,369 - 9 = \mathbf{24,360\text{ candidates per horizon}}$.
- **Total Trade Evaluations across 4 Horizons (5, 10, 20, 60)**: $24,360 \times 4 = \mathbf{97,440\text{ total evaluations}}$.
- **Line 221 Export Truncation**: `"history_records": all_history_signals[:25000]`. The payload caps `history_records` array at 25,000 items to constrain disk file size.
- **Array Ordering Limitation**: `all_history_signals` accumulates records in order of `symbols` processing (alphabetical symbol order) and chronological bar index $i$ per symbol. Therefore, `[:25000]` contains the first 25,000 generated records in symbol processing order, NOT strictly the most recent records chronologically across the entire dataset. `summary["total_evaluations"]` retains the true count **97,440**.

### E. Performance and Research Limitations
- **Realism Limitations**: Transaction costs, slippage, and market impact are NOT subtracted in `pnl_pct` calculation (`pnl_pct = round(((exit_price - entry_p) / entry_p) * 100, 2)`).
- **Conviction Score Derivation**: Calculated dynamically via `calculate_conviction_score()` in $[50.0, 95.0]$ based on RSI momentum, EMA alignment, and Donchian breakout clearance. It is a technical heuristic, NOT a calibrated statistical probability.
- **Out-of-Sample Limitations**: The walk-forward loop iterates sequentially day-by-day. However, strategy thresholds are fixed technical rules without an ML model training split.

---

## 3. Store Integrity & Tolerance Qualifications (Gate B)

Audit performed read-only across all **1,143,549 live DuckDB records** and **499 Parquet feature store files**:

- **DuckDB Invalid Cells (Null / NaN / Inf)**: **0 Cells**
- **Parquet Invalid Cells (Null / NaN / Inf)**: **0 Cells**
- **OHLC Geometry Violation Rows**: **0 Rows** in DuckDB, **0 Rows** in Parquet.
- **Non-Positive Price / Negative Volume Rows**: **0 Rows** in DuckDB, **0 Rows** in Parquet.
- **Duplicate (Symbol, Date) Primary Key Rows**: **0 Rows** in DuckDB, **0 Rows** in Parquet.
- **Bidirectional Symbol Set Equality**: **499 DuckDB symbols == 499 Parquet files** (0 extra in DuckDB, 0 extra in Parquet).
- **Numeric Tolerance Qualification**: Value comparison between DuckDB and Parquet stores matches within explicit numeric tolerance $< 10^{-4}$ (**`TOLERANCE MATCH < 1e-4`**), distinct from bitwise exact literal equality.

---

## 4. Universe Provenance and Historical-Coverage Limitations (Gates C & D)

- **Canonical Nifty 500 Universe**: 500 Equities ([nifty500_symbols.py](file:///D:/TradeMindAI/backend/app/db/nifty500_symbols.py)).
- **Full 10-Year History Equities (2015–2026)**: **306 Equities**
- **Post-2015 Listed Equities**: **193 Equities** (e.g. `ATGL` with 1,968 rows, `LICI` with 1,098 rows, `NYKAA`, `PAYTM`)
- **Unverified / Unlisted Equities**: **1 Equity (`BAGMANE`)** - Bagmane Developers Ltd., mapped in local universe source; Yahoo Finance ticker `BAGMANE.NS` returns no data.
- **Gate C Verdict**: **`UNVERIFIED`** (`BAGMANE` status unverified without local official constituent transition records).
- **Gate D Verdict**: **`PARTIAL / UNVERIFIED`** (Post-2015 start dates are observed start dates; official exchange listing calendar files unavailable locally).

---

## 5. Safety Invariants & Repository Preservation Evidence

- `REAL_TRADING = false` (Runtime value: `False`)
- `LIVE_EXECUTION_ENABLED = false` (Runtime value: `False`)
- `BROKER_ORDER_EXECUTION_ENABLED = false` (Runtime value: `False`)
- `QUARANTINE_ACTIVE = true` (Runtime value: `True`)
- **Qualification**: Runtime settings verification: PASS — the settings object returned the required values during this check. This result does not independently prove enforcement across every execution pathway.
- **Non-Interference Statement**: `NON-INTERFERENCE: NOT INDEPENDENTLY VERIFIABLE — authenticated before-and-after evidence is unavailable.`

---

## 6. Prioritized Evidence & Repair Plan (Awaiting Authorization)

1. **Prioritized Repair Action 1 (Universe Resolution)**: Clarify `BAGMANE` status by adding an explicit unlisted/delisted filter handling in `nifty500_symbols.py` once official exchange constituent transition evidence is supplied.
2. **Prioritized Repair Action 2 (Slippage & Cost Accounting)**: Incorporate optional 0.10% transaction cost & slippage deduction in backtest return calculations for real-world cost-sensitivity analysis.
3. **Prioritized Repair Action 3 (Export Pagination & Chronological Sorting)**: Sort `all_history_signals` chronologically by date prior to export and provide paginated JSON export or DuckDB table export for historical evaluations exceeding 25,000 records.

---

## 7. Final Release Decision

- **Overall Preservation Gate Verdict**: **`BLOCKED`** (Preservation Hold Active).
- **Confirmation**: Zero application code, databases, backup snapshot files, or frontend source files were modified, restored, or deleted during this task. Phase 1 TejHQ data provider integration remains blocked until explicit user instruction.

Deliverable report saved at:
- [FINAL_SIGNAL_METHODOLOGY_AND_PRESERVATION_AUDIT.md](file:///D:/TradeMindAI/reports/FINAL_SIGNAL_METHODOLOGY_AND_PRESERVATION_AUDIT.md)
