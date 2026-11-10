# TradeMindAI — Phase E Look-Ahead & Leakage Audit Report

**Audit Focus**: Look-ahead bias prevention, feature causality, unshifted rolling calculations, and training/test dataset leakage.

---

## 1. Causal Feature Engineering Rules

1. **Shifted Donchian Channels**: Structural high/low bounds are shifted 1 bar (`high.rolling(20).max().shift(1)`), ensuring bar $t$ cannot leak its own High/Low into its channel bounds.
2. **Point-in-Time Feature Slicing**: Slices feature data strictly at or before inference timestamp $t$ (`df[df.index <= timestamp]`).
3. **Incomplete Candle Exclusion**: Excludes incomplete active trading session candles from completed daily bar feature vectors.
4. **Purged Group Cross-Validation with Embargoing**: Function `MLService.purged_cross_validation_score()` enforces Marcos López de Prado's purged group splitting with a 5% embargo window between training and test sets to eliminate time-series label overlap leakage.

---

## 2. Test Verification Summary

- `test_phase_b_donchian_channels_shifted_causality`: **PASSED** (Zero look-ahead bias confirmed).
- `test_phase_e_incomplete_candle_filtering`: **PASSED**.
