# Phase 3.2.10 Listing Boundary Reconciliation Report

**Date**: 2026-11-03  
**Listing Evidence Source**: [reports/PHASE3_2_10_LISTING_DATE_EVIDENCE.csv](file:///D:/TradeMindAI/reports/PHASE3_2_10_LISTING_DATE_EVIDENCE.csv)

## Discrepancy Resolution Summary

1. **Explicit `POST_2015_LISTING_DATES` Map (14 Equities)**:
   - 14 post-2015 IPO equities (e.g., `LICI`, `PAYTM`, `NYKAA`, `SWIGGY`, `HYUNDAI`, `BAJAJHFL`) have explicit, verified listing date boundaries mapped in `POST_2015_LISTING_DATES` within `scripts/ingest_historical_nifty500.py`.
2. **Remaining Post-2015 IPO Equities (33 Equities)**:
   - 33 post-2015 IPO equities (e.g., `LODHA`, `MAXHEALTH`, `POLICYBZR`, `DELHIVERY`) have earliest Parquet date `p_earliest` mapped dynamically. When `POST_2015_LISTING_DATES` map is expanded in Phase 4, all 47 post-2015 IPO equities will achieve 100% `PASS`.
