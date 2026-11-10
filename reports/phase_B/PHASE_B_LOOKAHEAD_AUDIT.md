# TradeMindAI — Phase B Look-Ahead Bias & Point-in-Time Causality Audit Report

**Audit Focus**: Zero Look-Ahead Bias, Point-in-Time Causal Slicing, and Shifted Structural Levels

---

## 1. Point-in-Time Causality Principles

1. **Shifted Donchian Channels**:
   - `donchian_high_20` and `donchian_low_20` are calculated as `df['high'].rolling(window=20).max().shift(1)`.
   - The `.shift(1)` ensures that at time $t$, the channel boundaries are strictly derived from prices $t-20 \dots t-1$. Bar $t$'s own High/Low price cannot leak into its boundary calculation.
2. **Time-Safe Feature Slicing**:
   - In `FeatureStoreService.extract_institutional_features`, the input DataFrame is strictly sliced: `df_ta = df_ta[df_ta.index <= timestamp]`.
   - Feature extraction uses `df_ta.iloc[-1]`, preventing future bar leakages.
3. **Incomplete Current Candle Exclusion**:
   - Features for historical daily models are calculated on completed closed candles only (`bar_date <= as_of_completed_date`).

---

## 2. Test Verification Evidence

Function `test_phase_b_donchian_channels_shifted_causality` in `backend/tests/unit/test_phase_b_canonical_indicators.py`:
- Simulates a 30-bar price series where bar 30 experiences a major high price spike (500.0 vs prior 100.0).
- Confirms that at bar 30, `donchian_high_20` evaluates to **100.0** (derived from bars 10 to 29), proving zero look-ahead bias.
