# TradeMindAI — Phase F Indicator Certification Report

**Audited Component**: [backend/app/services/indicator_service.py](file:///D:/TradeMindAI/backend/app/services/indicator_service.py)

---

## 1. Canonical Indicator Audit Results

1. **RSI 14**:
   - `compute_wilder_rsi()` implements Wilder's Exponential Smoothing.
   - Requires 14 valid contiguous bars warm-up; returns `NaN` if $< 14$ bars.
   - Handles edge cases: positive gain/zero loss $\implies 100.0$, zero gain/positive loss $\implies 0.0$, flat $\implies 50.0$.
2. **EMA (20, 50, 100, 200)**:
   - `ema_200` requires $\ge 200$ bars history; returns `NaN` if $< 200$ bars.
3. **ATR 14**:
   - Rolling 14-bar True Range mean; returns `NaN` if $< 14$ bars.
   - No constant factor fallback ($0.02 \times \text{Price}$ is forbidden).
4. **Donchian Channels (20)**:
   - Shifted 1 bar (`shift(1)`) to guarantee zero look-ahead bias point-in-time causality.
5. **Column Normalization**:
   - Normalizes column names case-insensitively ("close", "Close", "high", "High", etc.).

---

## 2. Test Execution Evidence

- `test_phase_b_wilder_rsi_warmup_and_edge_cases`: **PASSED**
- `test_phase_b_rsi_period_validation`: **PASSED**
- `test_phase_b_ema200_warmup_guard`: **PASSED**
- `test_phase_b_donchian_channels_shifted_causality`: **PASSED**
- `test_phase_b_atr14_no_fabricated_fallback`: **PASSED**
- `test_phase_b_column_case_insensitivity`: **PASSED**
