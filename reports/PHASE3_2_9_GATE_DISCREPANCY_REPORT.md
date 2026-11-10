# Phase 3.2.9 Gate Discrepancy Reconciliation Report

**Date**: 2026-11-03  
**Status**: **100% RECONCILED**  
**Source Data**: [reports/PHASE3_2_9_GATE_DISCREPANCY_RECONCILIATION.csv](file:///D:/TradeMindAI/reports/PHASE3_2_9_GATE_DISCREPANCY_RECONCILIATION.csv)

## Discrepancy Resolution Summary

The discrepancy between the 242 gap-classification PASS symbols and the 241 overall PASS symbols was isolated:
- Ticker **`ICICIPRULI`** achieved `PASS` in historical daily validation, but had `UNSUPPORTED` 5m intraday quote data from Yahoo Finance provider API (`ICICIPRULI_5m.parquet` missing).
- Therefore, `ICICIPRULI`'s overall status is **`PARTIAL`**, bringing the overall `PASS` count to exactly **`241`**.

### Reconciled Symbol Summary

- **Overall `PASS`**: `241` symbols (100% complete historical, intraday, and storage consistency).
- **Overall `PARTIAL`**: `258` symbols (`47` post-2015 IPO listing boundaries + `210` missing 5m volume slots + `1` `ICICIPRULI` missing 5m quote).
- **Overall `UNSUPPORTED`**: `1` symbol (`BAGMANE` unlisted ticker).
- **Total Canonical Universe**: **`500` symbols** (`241 + 258 + 1 = 500`).
