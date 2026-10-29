# TradeMindAI R4.6.40 — Gate E1 (Incomplete Horizons) & Gate E2 (RSI Edge Cases) Forensic Audit Report

## 1. Executive Status & Verdict Matrix

**Overall Production Acceptance Status**: **`BLOCKED`** (Preservation Hold Active; Phase 1 TejHQ Integration Blocked)  
**Gate E1 (Incomplete Horizon Accounting)**: **`DEFECT DETECTED — PARTIAL / UNVERIFIED`** (Right-censored candidate signals with $1 \le len(future\_sub) < horizon$ that touch neither target nor stop are prematurely classified as `EXPIRED` at bar $N < horizon$, corrupting 20-day and 60-day horizon statistics)  
**Gate E2 (RSI Edge-Case Calculation)**: **`DEFECT DETECTED — PARTIAL / UNVERIFIED`** (`loss.replace(0, np.nan)` causes sustained rising series with $loss = 0$ to calculate RSI = 50.0 instead of 100.0, distorting momentum filter input)  
**Safety Invariants Status**: **`VERIFIED ENFORCED`** (`QUARANTINE_ACTIVE = true`, `REAL_TRADING = false`, `LIVE_EXECUTION_ENABLED = false`, `BROKER_ORDER_EXECUTION_ENABLED = false`)

---

## 2. Gate E1 — Incomplete Forward-Horizon Accounting Audit

Source Code Reference: [generate_walkforward_signals_duckdb.py:141-180](file:///D:/TradeMindAI/scripts/signals/generate_walkforward_signals_duckdb.py#L141-L180)

### A. Horizon Status Truth Table

| Scenario / Condition | `len(future_sub)` | Target Hit (+8%) | Stop Hit (-5%) | Actual Outcome in Code | True Mathematical Status | Impact & Distortion |
|---|---|---|---|---|---|---|
| **Completed Full Horizon** | `= horizon` | No | No | `EXPIRED` (at bar $horizon$) | `EXPIRED` | Correctly evaluated after full horizon window. |
| **Early Target Hit** | $1 \le N \le horizon$ | Yes | No | `TARGET_HIT` (at bar $N$) | `TARGET_HIT` | Correctly evaluated on hit bar. |
| **Early Stop Hit** | $1 \le N \le horizon$ | No | Yes | `STOP_LOSS` (at bar $N$) | `STOP_LOSS` | Correctly evaluated on hit bar. |
| **Right-Censored Incomplete Window** | $1 \le N < horizon$ | No | No | **`EXPIRED`** (at bar $N < horizon$) | **`RIGHT_CENSORED_INCOMPLETE`** | **DEFECT**: Classified as `EXPIRED` prematurely at bar $N < horizon$; corrupts 20-session and 60-session `EXPIRED` counts & PnL. |
| **Dataset Endpoint (Very Last Bar)** | `= 0` (`empty`) | N/A | N/A | **`ACTIVE`** (for horizon 20) | **`ACTIVE`** | Added to `active_buy_signals` for horizon 20. |

### B. Observed Code Behavior & Metric Impact
- **Lines 142–143**: `future_sub = df_sym.iloc[i+1 : i+1+horizon]`. `future_sub.empty` is True ONLY if signal $i$ occurs on the very last bar of `df_sym` (2026-10-27).
- **Right-Censoring Bug**: When signal $i$ occurs within $1$ to $horizon-1$ bars of dataset endpoint (e.g., 5 bars before 2026-10-27 for a requested 60-bar horizon), `future_sub` returns 5 bars. If neither target (+8%) nor stop (-5%) is hit in those 5 bars:
  - Line 150 initializes `status = "EXPIRED"`.
  - Line 151 sets `exit_price = float(future_sub.iloc[-1]["Close"])` (the price on day 5).
  - Line 176 computes 5-day PnL and records the signal in `all_history_signals` as a completed **60-session trade**!
- **Consequence**: Published 20-session and 60-session `EXPIRED` counts and average PnL figures include truncated right-censored trades.

---

## 3. Gate E2 — RSI Edge-Case Audit & Mathematical Behavior

Source Code Reference: [generate_walkforward_signals_duckdb.py:102-106](file:///D:/TradeMindAI/scripts/signals/generate_walkforward_signals_duckdb.py#L102-L106)

### A. Current Implementation Code
```python
delta = df_sym["Close"].diff()
gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
rs = gain / loss.replace(0, np.nan)
df_sym["rsi_14"] = 100 - (100 / (1 + rs)).fillna(50)
```

### B. Edge-Case Behavioral Analysis

| Market Price Series Scenario | `gain` Value | `loss` Value | Code Calculation | Calculated RSI | True Mathematical RSI | Defect Analysis |
|---|---|---|---|---|---|---|
| **Sustained Rising Series (14 Green Bars)** | $> 0$ | $= 0$ | `gain / np.nan` $\rightarrow$ `np.nan` $\rightarrow$ `fillna(50)` | **`50.0`** | **`100.0`** | **DEFECT**: Falsely assigns neutral 50.0 RSI to a perfectly bullish 100.0 breakout! |
| **Sustained Falling Series (14 Red Bars)** | $= 0$ | $> 0$ | `0 / loss` $\rightarrow$ `0.0` $\rightarrow$ `100 - 100` | **`0.0`** | **`0.0`** | Correctly evaluates to 0.0. |
| **Flat Series (Zero Price Change)** | $= 0$ | $= 0$ | `0 / np.nan` $\rightarrow$ `np.nan` $\rightarrow$ `fillna(50)` | **`50.0`** | **`50.0`** | Correctly evaluates to neutral 50.0. |
| **Mixed Gains and Losses** | $> 0$ | $> 0$ | `gain / loss` $\rightarrow$ standard RS | Standard | Standard | Correctly evaluates standard RSI. |

### C. Strategy Filter Consequence
- The strategy trigger requires `45.0 <= rsi <= 75.0` ([generate_walkforward_signals_duckdb.py:128](file:///D:/TradeMindAI/scripts/signals/generate_walkforward_signals_duckdb.py#L128)).
- A 14-bar parabolic breakout with $loss = 0$ has actual RSI = 100.0 (overbought). Because the code sets RSI = 50.0, it falsely passes the $[45, 75]$ filter!
- Conversely, if momentum threshold is adjusted to $>60$, a 100.0 RSI breakout is incorrectly filtered out because its calculated RSI was falsely set to 50.0.

---

## 4. Tests & Evidence Required Before Any Repair

To authorize a future repair phase (currently BLOCKED), the following tests must be created and verified:

1. **Unit Test 1 (`test_rsi_zero_loss_sustained_rise`)**: Verify that 14 consecutive green bars produce RSI = 100.0.
2. **Unit Test 2 (`test_rsi_zero_gain_sustained_fall`)**: Verify that 14 consecutive red bars produce RSI = 0.0.
3. **Unit Test 3 (`test_rsi_flat_series`)**: Verify that 14 flat bars produce RSI = 50.0.
4. **Unit Test 4 (`test_incomplete_horizon_censoring_exclusion`)**: Verify that signals with $len(future\_sub) < horizon$ and no target/stop hit are classified as `INCOMPLETE_WINDOW` and excluded from `EXPIRED` trade statistics for that horizon.

---

## 5. Safety Invariants & Release Decision

- `REAL_TRADING = false` (Runtime value: `False`)
- `LIVE_EXECUTION_ENABLED = false` (Runtime value: `False`)
- `BROKER_ORDER_EXECUTION_ENABLED = false` (Runtime value: `False`)
- `QUARANTINE_ACTIVE = true` (Runtime value: `True`)
- **Non-Interference Attribution**: `NON-INTERFERENCE: NOT INDEPENDENTLY VERIFIABLE — authenticated before-and-after evidence is unavailable.`
- **Overall Preservation Gate Verdict**: **`BLOCKED`** (Preservation Hold Active).
- **Confirmation**: Zero application code, databases, backup snapshot files, or frontend source files were modified during this audit. Phase 1 TejHQ data provider integration remains blocked until explicit user instruction.

Deliverable report saved at:
- [GATE_E_INCOMPLETE_HORIZON_AND_RSI_AUDIT.md](file:///D:/TradeMindAI/reports/GATE_E_INCOMPLETE_HORIZON_AND_RSI_AUDIT.md)
