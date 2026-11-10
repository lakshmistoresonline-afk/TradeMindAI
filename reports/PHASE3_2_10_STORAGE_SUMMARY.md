# Phase 3.2.10 Storage Summary Report

**Date**: 2026-11-03  
**Database Path**: `D:\TradeMindAI\backend\data\analytical.duckdb`  
**Features Path**: `D:\TradeMindAI\backend\data\features\`  
**Daily Source CSV**: [reports/PHASE3_2_10_DAILY_RECONCILIATION.csv](file:///D:/TradeMindAI/reports/PHASE3_2_10_DAILY_RECONCILIATION.csv)  
**Intraday Source CSV**: [reports/PHASE3_2_10_INTRADAY_RECONCILIATION.csv](file:///D:/TradeMindAI/reports/PHASE3_2_10_INTRADAY_RECONCILIATION.csv)

## Storage Summary Breakdown

- **Daily Storage**: `499` `DAILY_PASS` (100% key and value equality), `1` `UNSUPPORTED_WITH_EVIDENCE` (`BAGMANE`), `0` `DAILY_FAIL`.
- **Intraday Storage**: `498` `INTRADAY_PASS` (100% key and value equality), `1` `INTRADAY_FILE_MISSING` (`ICICIPRULI`), `1` `UNSUPPORTED_WITH_EVIDENCE` (`BAGMANE`), `0` `INTRADAY_FAIL`.
- **Numeric Tolerance**: `1e-4` (maximum absolute OHLCV difference observed across all 498 matching tickers is `0.000000`).
