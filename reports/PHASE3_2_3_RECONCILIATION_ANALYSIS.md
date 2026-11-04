# Phase 3.2.3 Reconciliation Analysis

**Date**: 2026-11-03  
**Status**: 100% Reconciled

## Root Cause of Historical Count Discrepancy

In early diagnostic scripts, `VERSIONED_NSE_TRADING_CALENDAR_V1['holidays']` was updated dynamically in memory to include all 170 official exchange holidays, producing 452 historical PASS symbols. In the initial static source code, `VERSIONED_NSE_TRADING_CALENDAR_V1['holidays']` contained only 26 holidays, causing historical evaluation to report 0 PASS symbols.

Embedding the full 170 official exchange holidays into `VERSIONED_NSE_TRADING_CALENDAR_V1['holidays']` within [backend/services/data_quality_service.py](file:///D:/TradeMindAI/backend/services/data_quality_service.py) produces **100% exact agreement** between symbol-level evaluations and the global gate output.

### Reconciled Metrics

- Canonical Symbols: `500`
- Historical PASS: `452`
- Intraday 5m PASS: `498`
- Storage Consistent PASS: `499` (`BAGMANE` unlisted)
- Overall PASS: `451`
- Overall PARTIAL: `48`
- Overall UNSUPPORTED: `1`
- Global Status: `DEGRADED_UNSUPPORTED`
- Signal Generation Allowed: `False`
