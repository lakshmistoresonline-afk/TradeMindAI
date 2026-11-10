# Phase 4 PARTIAL Symbols Diagnostic Report

**Date**: 2026-11-03  
**Diagnostic CSV**: [reports/PHASE4_258_PARTIAL_SYMBOLS_DIAGNOSTIC.csv](file:///D:/TradeMindAI/reports/PHASE4_258_PARTIAL_SYMBOLS_DIAGNOSTIC.csv)  
**Status**: **AUDITED (500 Symbols Evaluated)**

## Summary of Constituent Coverage Audit

- **Canonical NIFTY 500 Universe Size**: 500
- **COMPLETE Symbols (`PASS`)**: Benchmark equities with 100% daily and intraday coverage (e.g. `RELIANCE`, `TCS`, `INFY`, `HDFCBANK`).
- **PARTIAL Symbols**: Equities containing minor intraday 5m candle gaps from Yahoo Finance provider quotes or post-2015 IPO listing boundaries.
- **UNSUPPORTED Symbols**: `BAGMANE` (unlisted ticker on Yahoo Finance API `BAGMANE.NS`).
- **Repair Requirement**: Ingestion manifest created in `DataRepairPlannerService` for FYERS / Angel One API backfill.
