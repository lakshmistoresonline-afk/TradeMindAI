# Phase 3.2.9 Provider Support Evidence Report

**Date**: 2026-11-03  
**Evaluated Data Provider**: Yahoo Finance API (`yfinance` v0.2.x)

## Evidence & Provider Limitations

1. **Unlisted Instrument (`BAGMANE`)**:
   - `BAGMANE.NS` returns `HTTP 404 Not Found` / `No data found, symbol may be delisted`.
   - Classification: `UNSUPPORTED_PROVIDER_SYMBOL`. Symbol retained in canonical 500 universe.

2. **Intraday Quote API Errors (`ICICIPRULI`)**:
   - `ICICIPRULI.NS` 5m intraday quote returns `KeyError('tradingPeriods')` from provider API.
   - Classification: `MISSING_PROVIDER_DATA`.

3. **Post-2015 IPO Listings**:
   - Tickers like `LICI` (listed May 2022), `PAYTM` (listed Nov 2021), `NYKAA` (listed Nov 2021), `SWIGGY` (listed Nov 2024), `HYUNDAI` (listed Oct 2024), `BAJAJHFL` (listed Sep 2024) have zero data prior to their official IPO listing date on NSE.
