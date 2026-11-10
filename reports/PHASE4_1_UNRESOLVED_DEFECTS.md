# Phase 4.1 Unresolved Defects & Open Action Items Report

**Date**: 2026-11-03  
**Status**: Zero Software Defects / Action Items Identified for Operator

## Actions Requiring Operator Authorization

1. **Supply FYERS / Angel One API Credentials**: Configure `FYERS_CLIENT_ID` / `FYERS_ACCESS_TOKEN` in environment variables.
2. **Execute Controlled Data Repair Batch**: Call `POST /api/v1/market-data/providers/repair/execute?max_symbols=500` to backfill missing 5m candles into DuckDB/Parquet for the 79 PARTIAL stocks.
3. **Execute Production Signal Scan**: Once Global Data Gate evaluates `signal_generation_allowed = True`, authorize `EquitySignalGenerationService.run_production_scan()`.
