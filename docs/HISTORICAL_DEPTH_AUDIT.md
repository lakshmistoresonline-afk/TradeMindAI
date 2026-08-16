# Historical Data Depth Audit

**Audit Timestamp**: 2026-08-16 12:55:00 UTC
**Status**: PASS

## 1. Distribution Summary

| Metric | Value |
| :--- | :--- |
| Total Symbols Audited | 199 |
| Symbols with 6-Year History (2020+) | 188 |
| Symbols with 2-Year History (2024+) | 196 |
| Symbols with < 1 Year (Recent Listing) | 3 |
| Total Market Candles Ingested | 318,364 |

## 2. Coverage Analysis
- **Full History**: 188/200 symbols have continuous daily candles from January 1, 2020, to August 14, 2026.
- **Valid Short History**: 11 symbols have shorter histories due to listing dates (e.g., LICI, NYKAA, PAYTM) or demergers (e.g., TATAMOTORS/TMCV).
- **Data Unavailable**: 1 symbol (LTIM) remains unavailable from approved providers in the Aug 2026 timeline.

## 3. Data Integrity
- **Fabrication**: ZERO synthetic or placeholder candles detected.
- **OHLC Validation**: All 318,364 candles passed non-negative price and volume checks.
- **Timezone**: Consistent UTC (IST-5.5h) across the entire dataset.
