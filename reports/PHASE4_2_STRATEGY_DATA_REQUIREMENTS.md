# Phase 4.2 Strategy Data Requirements Report

**Date**: 2026-11-03  
**Target File**: [backend/services/equity_signal_generation_service.py](file:///D:/TradeMindAI/backend/services/equity_signal_generation_service.py)

## Strategy Horizon Requirements

| Strategy Horizon | Required Data Input | Minimum Required History | Fail-Closed Policy |
| :--- | :--- | :--- | :--- |
| **SHORT** | 5-Minute Intraday & Daily | 200 bars 5m intraday | `INSUFFICIENT_INTRADAY_DATA` if missing 5m candles |
| **SWING** | Daily & Intraday 5m | 200 bars daily + 5m intraday | `INSUFFICIENT_DAILY_DATA` if missing daily/intraday |
| **LONG** | Daily OHLCV | 200 bars daily | `INSUFFICIENT_DAILY_DATA` if history < 200 daily bars |
