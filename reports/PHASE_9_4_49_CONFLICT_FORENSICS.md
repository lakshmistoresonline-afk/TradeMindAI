# TradeMindAI — Phase 9.4.49 Historical Price Conflict Forensics Report

**Date:** October 17, 2026  
**Repository:** `D:\TradeMindAI`  
**Auditor:** Quantitative Systems Verification Taskforce  
**Status:** **`COMPLETED_READ_ONLY_FORENSICS`**

---

## 1. Executive Summary

This forensics report presents read-only findings from inspecting the `historical_prices` table in `PriceDB`. 

- **Total Table Rows**: **4,337,761**
- **Direct SQL Distinct Composite Keys `(symbol, date, source)`**: **2,937,726**
- **Duplicate Key Groups Count**: **809,251**
- **Participating Rows in Duplicate Groups**: **2,209,286**
- **Excess Duplicate Rows**: **1,400,035**
- **Null-Safe Exhaustive Group Classification**:
  - **Identical Duplicate Groups**: **809,251 (100.00%)**
  - **Conflicting Duplicate Groups**: **0 (0.00%)**
  - **Indeterminate Duplicate Groups**: **0 (0.00%)**

---

## 2. Forensic Analysis of Sample Equities

Representative sample equities evaluated read-only in `PriceDB`:
- **RELIANCE**: 6,154 raw records $\rightarrow$ 6,154 distinct dates $\rightarrow$ 6,154 usable daily bars after collapsing identical duplicate rows.
- **TCS**: 6,154 raw records $\rightarrow$ 6,154 distinct dates $\rightarrow$ 6,154 usable daily bars.
- **INFY**: 6,154 raw records $\rightarrow$ 6,154 distinct dates $\rightarrow$ 6,154 usable daily bars.
- **HDFCBANK**: 6,154 raw records $\rightarrow$ 6,154 distinct dates $\rightarrow$ 6,154 usable daily bars.
- **ICICIBANK**: 6,154 raw records $\rightarrow$ 6,154 distinct dates $\rightarrow$ 6,154 usable daily bars.

---

## 3. Reconciliation Policy Summary

1. **Identical Duplicates**: Collapsed to 1 clean daily bar per date in production preparation pipeline.
2. **Conflicting Records**: If differing OHLCV values occur for the same symbol/date, `prepare_reconciled_daily_bars` flags the date as `BLOCKED_DUPLICATE_CONFLICT` and excludes it from indicator inputs.
3. **Indicator Calculation**: Executed strictly on reconciled, deduplicated, chronologically ordered daily bars.
