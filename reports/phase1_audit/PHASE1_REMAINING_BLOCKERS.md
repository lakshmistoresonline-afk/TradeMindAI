# Phase 1 — Remaining Blockers and Unresolved Risks

## Active Release Blockers

### 1. `BAGMANE` Universe Constituent Transition Verification (Gate 2 & Gate 11)
- **Problem**: Stock symbol `BAGMANE` is unlisted/delisted on Yahoo Finance API (`BAGMANE.NS`).
- **Affected File**: `backend/app/db/nifty500_symbols.py`
- **Root Cause**: External API provider returns no price/volume data for `BAGMANE.NS`.
- **Required Resolution**: Official exchange constituent transition records from NSE are required before modifying universe definition.

### 2. Historical Signal Ledger Export Preservation Hold
- **Problem**: `backend/data/signals_history.json` and backtest trade records remain under preservation hold.
- **Affected File**: `backend/data/signals_history.json`
- **Root Cause**: Production signal re-export/regeneration is prohibited until Phase 1 data integrity is fully authorized.
- **Required Resolution**: Explicit authorization to run historical signal export after Phase 1 release gate sign-off.
