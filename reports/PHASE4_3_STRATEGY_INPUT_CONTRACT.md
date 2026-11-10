# Phase 4.3 Strategy Input Contract Report

**Date**: 2026-11-03  
**Status**: **VERIFIED**

## Strategy Horizon Input Specifications

| Horizon | Data Input Required | Minimum Lookback | Feature Inputs | Rejection Code when Missing |
| :--- | :--- | :---: | :--- | :--- |
| **SHORT** | Intraday 5m & Daily | 200 5m bars | `Open, High, Low, Close, Volume, ATR, RSI, EMAs` | `INSUFFICIENT_INTRADAY_DATA` |
| **SWING** | Daily & Intraday 5m | 200 daily bars | `Open, High, Low, Close, Volume, ATR, RSI, EMAs` | `INSUFFICIENT_DAILY_DATA` |
| **LONG** | Daily OHLCV | 200 daily bars | `Open, High, Low, Close, Volume, ATR, RSI, EMAs` | `INSUFFICIENT_DAILY_DATA` |
