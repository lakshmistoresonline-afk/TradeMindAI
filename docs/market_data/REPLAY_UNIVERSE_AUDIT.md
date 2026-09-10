# REPLAY UNIVERSE AUDIT

## 1. Membership Summary
- **Total NIFTY-200 Constituents**: 200
- **Champion Models Registered**: 101
- **Symbols with Sufficient History (>150 days)**: 200
- **Symbols Scanned in Replay**: 50 (Batch 1 & 2)
- **Symbols with Generated Signals**: 6

## 2. Selection Bias / Rejection Reasons
The low signal frequency in the historical replay (6/50 symbols) is attributed to the strict production gates of Strategy V2.2:

| Symbol | Scanned | Signals | Status | Primary Rejection Reason |
| :--- | :--- | :--- | :--- | :--- |
| **RELIANCE** | YES | 7 | ACTIVE | TREND_CONFLICT_BEARISH (recent) |
| **ICICIBANK**| YES | 2 | RESOLVED | TREND_CONFLICT_BULLISH (previous) |
| **INFY** | YES | 0 | NO_TRADE | WEAK_EDGE |
| **TCS** | YES | 0 | NO_TRADE | TREND_CONFLICT_BEARISH |
| **HDFCBANK** | YES | 0 | NO_TRADE | TREND_CONFLICT_BEARISH |

## 3. Conclusion
The historical replay universe is currently limited to symbols with registered Champion Models. The low match rate confirms the strategy's high selectivity in the tested 180-day window.

---
**Status**: AUDITED.
