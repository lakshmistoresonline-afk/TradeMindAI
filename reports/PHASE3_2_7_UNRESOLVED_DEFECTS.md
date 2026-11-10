# Phase 3.2.7 Unresolved Defects & Data Gaps Report

**Date**: 2026-11-03  
**Status**: Documented & Tracked for Phase 4 Data Ingestion

## Inventory of Remaining Data Gaps

1. **Unlisted Ticker (`BAGMANE`)**:
   - *Status*: Unlisted on Yahoo Finance provider API (`BAGMANE.NS`).
   - *Classification*: `UNSUPPORTED_PROVIDER_SYMBOL`. Preserved in canonical 500 universe list.

2. **Post-2015 IPO Listing Boundaries (47 Equities)**:
   - *Status*: Equities listed after 2015 (e.g. `LICI`, `PAYTM`, `NYKAA`, `SWIGGY`, `HYUNDAI`, `BAJAJHFL`) have valid earliest dates corresponding to their actual IPO listing dates.
   - *Classification*: `POST_2015_IPO_LISTING_BOUNDARY`; require Phase 4 listing boundary mapping.

3. **Intraday 5m Volume Slot Gaps (210 Equities)**:
   - *Status*: Illiquid 5m volume slots or provider API quote limits.
   - *Classification*: `MISSING_PROVIDER_DATA`; require Phase 4 provider multi-quote backfill.
