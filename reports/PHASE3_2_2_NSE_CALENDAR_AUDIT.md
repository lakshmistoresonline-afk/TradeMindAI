# Phase 3.2.2 NSE Calendar Audit

**Calendar Version**: `VERSIONED_NSE_TRADING_CALENDAR_V1` (v1.0.0)  
**Total Holidays Embedded**: 170 official exchange holidays (2015–2026)  
**Evidence Source**: [reports/PHASE3_2_2_NSE_CALENDAR_EVIDENCE.csv](file:///D:/TradeMindAI/reports/PHASE3_2_2_NSE_CALENDAR_EVIDENCE.csv)

## Key Validation Findings

1. **Official Exchange Notices**: All 170 holidays map to verified NSE circulars spanning 2015 to 2026.
2. **Special Sessions**: Evening Muhurat trading sessions (e.g., 2025-10-21 18:15 IST and 2026-11-08 18:15 IST) are classified explicitly as special 13-slot sessions.
3. **Weekend Closures**: All Saturdays and Sundays are excluded from regular expected business trading session calculations.
