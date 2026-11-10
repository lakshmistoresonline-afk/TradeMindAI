# TradeMindAI — Phase B Master Indicator Audit Report

**Audit Scope**: Technical indicator calculations, warm-up policies, look-ahead bias prevention, feature consistency across signal generation, model training, historical backtesting, and shadow evaluation pipelines.  
**Repository**: `D:\TradeMindAI`  
**Phase Verdict**: **`PHASE B BLOCKED`** (Canonical indicator module verified; protected file fallback in `signal_engine.py` blocked pending authorization)

---

## 1. Executive Summary

Phase B performed a quantitative audit of technical indicator implementations across TradeMindAI. All 5 mandatory product safety invariants remain 100% enforced (`REAL_TRADING = False`, `LIVE_EXECUTION_ENABLED = False`, `BROKER_ORDER_EXECUTION_ENABLED = False`, `QUARANTINE_ACTIVE = True`, `SIGNALS_ONLY_ARCHITECTURE = True`).

### Key Audit Findings

| Pipeline / Module | File Reference | RSI Formula | EMA 200 Warm-Up Guard | ATR Fallback | Donchian Causality | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :---: |
| **Canonical Indicator Module** | [backend/app/services/indicator_service.py](file:///D:/TradeMindAI/backend/app/services/indicator_service.py) | Wilder Exponential Smoothing | Strict (`len >= 200`, returns `NaN` if insufficient) | Strict True Range rolling mean (returns `NaN` if `< 14` bars) | 1-bar shift (`shift(1)`) zero look-ahead | **VERIFIED** |
| **Research Feature Engine** | [backend/analysis/research_features.py](file:///D:/TradeMindAI/backend/analysis/research_features.py) | `pandas_ta` / `ta` Wilder | Strict history validation (`len >= 55`) | Strict `pta.atr` | 1-bar shift (`shift(1)`) zero look-ahead | **VERIFIED** |
| **Feature Store Service** | [backend/services/feature_store.py](file:///D:/TradeMindAI/backend/services/feature_store.py) | Canonical `momentum_rsi` | NaN for missing values; no silent zeroing | Strict ATR | PIT-safe slicing (`index <= timestamp`) | **VERIFIED** |
| **Protected Signal Engine Fallback** | [backend/services/signal_engine.py#L50-L95](file:///D:/TradeMindAI/backend/services/signal_engine.py#L50) | Simple rolling mean | `close.ewm(span=200)` without warm-up guard | Fabricated `0.02 * close` fallback | Unshifted | **BLOCKED** (Protected file) |

---

## 2. Inconsistent Fallback Defect in Protected File

- **File Reference**: [backend/services/signal_engine.py](file:///D:/TradeMindAI/backend/services/signal_engine.py#L50-L95)
- **Defect Description**: When `features_list` is empty, `SignalEngine.generate_signal` executes an in-line dynamic fallback calculation:
  - Uses simple rolling mean RSI: `gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()` instead of Wilder Exponential Smoothing.
  - Calculates `ema_200` without checking `len(df) >= 200`.
  - Replaces missing indicator values with zero: `df = df.fillna(0)`.
  - Fabricates ATR fallback: `"ATR": float(last_row['ATR'] if last_row['ATR'] > 0 else last_row['close'] * 0.02)`.
  - Fabricates RSI fallback: `"RSI": float(last_row['RSI'] if last_row['RSI'] > 0 else 50.0)`.
- **Protected File Restriction**: `backend/services/signal_engine.py` is protected by safety rules and cannot be modified.
- **Action Taken**: Documented finding and marked blocked pending explicit stakeholder authorization to patch `signal_engine.py`.
