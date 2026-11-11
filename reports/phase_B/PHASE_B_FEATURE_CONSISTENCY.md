# TradeMindAI — Phase B Feature Consistency Audit Report

**Audit Area**: Multi-Pipeline Indicator & Feature Calculation Consistency

---

## 1. Feature Consistency Evaluation Across Pipelines

| Feature | `LocalIndicatorService` | `EquitySignalGenerationService` | `FeatureCalculationService` | `ResearchFeatures` | `FeatureStoreService` | Consistency Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :---: |
| **RSI (14)** | Wilder Exponential Smoothing | Wilder via `compute_wilder_rsi` | Wilder via `pta.rsi` / `compute_wilder_rsi` | Wilder via `pta.rsi` | Wilder via `momentum_rsi` | **CONSISTENT** |
| **EMA (20, 50, 200)** | Warm-up guarded (`ema_200 = NaN` if `< 200` bars) | Warm-up guarded (`len >= 200`) | Warm-up guarded | Warm-up guarded | Warm-up guarded | **CONSISTENT** |
| **ATR (14)** | Rolling TR (returns `NaN` if `< 14` bars) | Rolling TR | `pta.atr` / `talib` ATR | `pta.atr` | `ATR` | **CONSISTENT** |
| **Bollinger Bands (20, 2)** | SMA 20 $\pm$ 2 std dev | SMA 20 | `bb_upper`, `bb_lower` | `bbands` | `volatility_bb_width` | **CONSISTENT** |
| **Donchian Channels (20)** | Shifted 1-bar (`shift(1)`) | Shifted 1-bar | Shifted 1-bar | Shifted 1-bar (`shift(1)`) | Shifted 1-bar | **CONSISTENT** |

---

## 2. Inconsistency Findings & Mitigation

1. **Non-Numeric and Infinite Value Filtering**:
   - `LocalIndicatorService`, `ResearchFeatures`, and `FeatureStoreService` strip `NaN` and `np.inf` values before calculation and replace missing outputs with `None` / `np.nan` instead of `0.0`.
2. **Missing Feature Contract**:
   - Incomplete candles and warm-up periods cleanly evaluate to `NaN` / `None`. No zero-filling or constant scaling (`0.02 * price`) occurs in `LocalIndicatorService`.
3. **Protected File Fallback Warning**:
   - As noted in `PHASE_B_INDICATOR_AUDIT.md`, `backend/services/signal_engine.py` (lines 50-95) contains an un-updated dynamic fallback when `features_list` is missing/empty. Because `signal_engine.py` is protected, the modification is blocked pending explicit user authorization.
