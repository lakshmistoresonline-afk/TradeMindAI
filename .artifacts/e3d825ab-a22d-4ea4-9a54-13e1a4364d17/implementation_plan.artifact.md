# Implementation Plan - STEP 4.5.2 MARKET-CALENDAR-AWARE SHADOW EXECUTION

This plan implements an intelligent market-aware workflow for shadow trading, distinguishing between different market sessions and handling EOD reconciliation.

## 1. Objectives
- **Market Awareness**: Implement precise tracking of Indian market sessions (Open, Closed, Pre/Post, Holiday, Weekend).
- **Session-Specific Workflows**: Create separate scripts for Intraday (Signal Generation) and EOD (Reconciliation/Equity updates).
- **Data Integrity**: Audit and document invalid symbols in the NIFTY 200 universe.
- **Enhanced Visibility**: Prominently display market status and diagnostic scores on the dashboard.

## 2. Proposed Changes

### [MODIFY] [backend/services/market_calendar.py](file:///G:/TradeMindAI/backend/services/market_calendar.py)
- Refactor `IndianMarketCalendar` to include:
    - List of observed 2026 NSE holidays.
    - `get_current_session()` method returning `OPEN`, `CLOSED`, `PRE_MARKET`, `POST_MARKET`, `HOLIDAY`, `WEEKEND`.
    - Improved `get_data_freshness_status` logic.

### [NEW] [docs/step4_5/INVALID_SYMBOL_AUDIT.md](file:///G:/TradeMindAI/docs/step4_5/INVALID_SYMBOL_AUDIT.md)
- Audit of the 4 invalid symbols (`GUJGASLTD`, `LTIM`, `PEL`, `TATAMOTORS`).
- Detail missing fields, date ranges, and reasons for failure.

### [MODIFY] [scripts/accuracy/step4_5_shadow_engine.py](file:///G:/TradeMindAI/scripts/accuracy/step4_5_shadow_engine.py)
- Update `run_cycle()` to accept a `mode` parameter (`intraday` or `eod`).
- In `intraday` mode: Generate signals only if `OPEN`.
- In `eod` mode: Perform full position reconciliation using latest prices and update daily equity.
- Log session type and market status in diagnostics.

### [MODIFY] [scripts/accuracy/step4_5_firebase_sync.py](file:///G:/TradeMindAI/scripts/accuracy/step4_5_firebase_sync.py)
- Include `market_status` and `session_type` in the `shadow_summary/latest` document.
- Sync detailed diagnostics including session context.

### [NEW] [scripts/windows/STEP4_5_SHADOW_INTRADAY.ps1](file:///G:/TradeMindAI/scripts/windows/STEP4_5_SHADOW_INTRADAY.ps1)
- Master runner for active market hours.
- Exits with `MARKET_CLOSED` if not in an `OPEN` session.

### [NEW] [scripts/windows/STEP4_5_SHADOW_EOD.ps1](file:///G:/TradeMindAI/scripts/windows/STEP4_5_SHADOW_EOD.ps1)
- Master runner for post-market reconciliation.
- Forces equity update and generates the daily summary report.

## 3. Verification Plan

### Automated Tests
- Run `verify_firebase_shadow.py` to confirm `market_status` field exists in Firestore.
- Assert `ShadowScanDiagnosticDB` records the correct `rejection_reason` for a closed market.

### Manual Verification
- Execute `STEP4_5_SHADOW_EOD.ps1` and verify the `shadow_equity` history update.
- Check the Dashboard (if connected) for the new Market Status badge.

## 4. Hard Constraints
- **FROZEN Strategy**: No changes to v2.2 logic (Target, Stop, Threshold, Model).
- **Local Only**: 100% Windows execution.
