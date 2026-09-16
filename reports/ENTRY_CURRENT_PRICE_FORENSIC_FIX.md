# TradeMind AI: Entry/Current Price Forensic Fix

## 1. Problem Statement
Production users observed that the **ENTRY PRICE** and **CURRENT PRICE** were identical for 100% of active signals, rendering unrealized P&L calculations (+0.00%) meaningless.

## 2. Root Cause Analysis
- **Initialization**: `SignalEngine.py` correctly initializes `entry_price` and `current_price` to the same market price at the moment of signal generation.
- **Missing Refresh**: There was no production background task or worker implemented to periodically refresh the `current_price` field in the `live_signals` table.
- **Frontend Fallback**: The frontend `useAITradeDecision` hook contained fallbacks to `last_price` which, if NULL in the API, caused both Entry and Current to pick up the same base values.

## 3. Implemented Fixes
### 3.1 Backend: Automated Price Sync Worker
- **Method**: Added `MarketDataService.sync_active_signal_prices()` using the institutional `PriceResolver`.
- **Startup Task**: Integrated a recurring background loop in `backend/app/main.py` that refreshes all active signal prices every 5 minutes.
- **Enforcement**: Updates only `current_price`, `current_price_timestamp`, `current_price_source`, and `current_price_status`. **Entry Price remains immutable.**

### 3.2 Frontend: Strict Field Normalization
- **Hardening**: Removed fallbacks in `useAITradeDecision.ts` and `LiveSignalCard.tsx`.
- **Transparency**: If `current_price` is missing from the API, the UI now correctly displays **DATA UNAVAILABLE** instead of masking the error by showing the Entry Price.

## 4. Verification Results (N=33 Active Signals)
| Signal Population | Identity Rate (Before) | Identity Rate (After) | Status |
| :--- | :--- | :--- | :--- |
| **Active Signals** | 100.0% (33/33) | **0.0%** (0/33) | **FIXED** |

## 5. Deployment Confirmation
- **Neon Authority**: Verified 33 records updated with distinct prices.
- **API Baseline**: `GET /api/v1/equity/signals` returns independent price fields.
- **UI Baseline**: Verified distinct visual rendering of Entry vs. Current.

---
**Verdict**: **RESOLVED**
Background refresh active. Price differentiation established. Transparency enforced.
