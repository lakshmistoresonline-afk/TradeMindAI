# Phase 3.2.11 Listing Boundary Report

**Date**: 2026-11-03  
**Listing Evidence Source**: [reports/PHASE3_2_11_LISTING_DATE_EVIDENCE.csv](file:///D:/TradeMindAI/reports/PHASE3_2_11_LISTING_DATE_EVIDENCE.csv)

## Listing Boundary Summary

1. **Explicit `POST_2015_LISTING_DATES` Map (14 Equities)**:
   - 14 post-2015 IPO equities (e.g., `LICI`, `PAYTM`, `NYKAA`, `SWIGGY`, `HYUNDAI`, `BAJAJHFL`) have explicit, verified listing date boundaries mapped in `POST_2015_LISTING_DATES` within `scripts/ingest_historical_nifty500.py`.
2. **Remaining Post-2015 IPO Equities (33 Equities)**:
   - 33 post-2015 IPO equities (e.g., `LODHA`, `MAXHEALTH`, `POLICYBZR`, `DELHIVERY`) have earliest Parquet date `p_earliest` mapped dynamically.
