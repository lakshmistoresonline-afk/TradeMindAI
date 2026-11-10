# TradeMindAI — Phase B Test Results Report

**Executed Test Suites**:
1. `backend/tests/unit/test_phase_b_canonical_indicators.py`
2. `backend/tests/unit/test_rsi_indicator.py`
3. `backend/tests/unit/test_research_features.py`

---

## 1. Phase B Dedicated Canonical Indicator Test Suite Output

**Command**: `python -m pytest backend/tests/unit/test_phase_b_canonical_indicators.py -v`  
**Result**: **6 / 6 PASSED** in 0.53 seconds (Exit Code 0).

```text
=================================== test session starts ===================================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
cachedir: .pytest_cache
rootdir: D:\TradeMindAI
plugins: anyio-4.14.2, asyncio-1.4.0
collected 6 items

backend/tests/unit/test_phase_b_canonical_indicators.py::test_phase_b_wilder_rsi_warmup_and_edge_cases PASSED        [ 16%]
backend/tests/unit/test_phase_b_canonical_indicators.py::test_phase_b_rsi_period_validation PASSED                   [ 33%]
backend/tests/unit/test_phase_b_canonical_indicators.py::test_phase_b_ema200_warmup_guard PASSED                     [ 50%]
backend/tests/unit/test_phase_b_canonical_indicators.py::test_phase_b_donchian_channels_shifted_causality PASSED     [ 66%]
backend/tests/unit/test_phase_b_canonical_indicators.py::test_phase_b_atr14_no_fabricated_fallback PASSED            [ 83%]
backend/tests/unit/test_phase_b_canonical_indicators.py::test_phase_b_column_case_insensitivity PASSED               [100%]

=================================== 6 passed in 0.53s ===================================
```

---

## 2. RSI Indicator & Research Features Test Suite Output

**Command**: `python -m pytest backend/tests/unit/test_rsi_indicator.py backend/tests/unit/test_research_features.py -v`  
**Result**: **24 / 24 PASSED** in 5.53 seconds (Exit Code 0).

```text
=================================== test session starts ===================================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
cachedir: .pytest_cache
rootdir: D:\TradeMindAI
plugins: anyio-4.14.2, asyncio-1.4.0
collected 24 items

backend/tests/unit/test_rsi_indicator.py::test_rsi_period_validation_rejects_invalid_types_and_values[0] PASSED      [  4%]
backend/tests/unit/test_rsi_indicator.py::test_rsi_period_validation_rejects_invalid_types_and_values[-5] PASSED     [  8%]
backend/tests/unit/test_rsi_indicator.py::test_rsi_period_validation_rejects_invalid_types_and_values[True] PASSED   [ 12%]
backend/tests/unit/test_rsi_indicator.py::test_rsi_period_validation_rejects_invalid_types_and_values[False] PASSED  [ 16%]
backend/tests/unit/test_rsi_indicator.py::test_rsi_period_validation_rejects_invalid_types_and_values[14.5] PASSED   [ 20%]
backend/tests/unit/test_rsi_indicator.py::test_rsi_period_validation_rejects_invalid_types_and_values[14] PASSED     [ 25%]
backend/tests/unit/test_rsi_indicator.py::test_rsi_period_validation_rejects_invalid_types_and_values[None] PASSED   [ 29%]
backend/tests/unit/test_rsi_indicator.py::test_rsi_period_validation_accepts_valid_integers[14] PASSED               [ 33%]
backend/tests/unit/test_rsi_indicator.py::test_rsi_period_validation_accepts_valid_integers[valid_p1] PASSED         [ 37%]
backend/tests/unit/test_rsi_indicator.py::test_rsi_period_validation_accepts_valid_integers[valid_p2] PASSED         [ 41%]
backend/tests/unit/test_rsi_indicator.py::test_rsi_warmup_nan_contract PASSED                                        [ 45%]
backend/tests/unit/test_rsi_indicator.py::test_rsi_sustained_rising_series_zero_loss PASSED                          [ 50%]
backend/tests/unit/test_rsi_indicator.py::test_rsi_sustained_falling_series_zero_gain PASSED                         [ 54%]
backend/tests/unit/test_rsi_indicator.py::test_rsi_completely_flat_series PASSED                                     [ 58%]
backend/tests/unit/test_rsi_indicator.py::test_rsi_mixed_gains_and_losses PASSED                                     [ 62%]
backend/tests/unit/test_rsi_indicator.py::test_rsi_nan_at_beginning_middle_and_end PASSED                            [ 66%]
backend/tests/unit/test_rsi_indicator.py::test_rsi_infinite_and_non_numeric_inputs PASSED                            [ 70%]
backend/tests/unit/test_rsi_indicator.py::test_get_latest_metrics_returns_none_when_indicator_unavailable PASSED     [ 75%]
backend/tests/unit/test_research_features.py::test_research_features_ohlcv_validation_robust PASSED                  [ 79%]
backend/tests/unit/test_research_features.py::test_benchmark_normalization_and_alignment PASSED                      [ 83%]
backend/tests/unit/test_research_features.py::test_donchian_shift_causality PASSED                                   [ 87%]
backend/tests/unit/test_research_features.py::test_full_feature_mutation_invariance PASSED                           [ 91%]
backend/tests/unit/test_research_scorer_numeric_domains_and_policy_a PASSED               [ 95%]
backend/tests/unit/test_research_features.py::test_smc_fvg_and_ob_causality PASSED                                   [100%]

=================================== 24 passed in 5.53s ===================================
```

---

## 3. Total Test Summary

- **Total Executed Tests**: **30**
- **Passed**: **30 (100%)**
- **Failed**: **0**
