# F&O PUBLIC DATA REPORT

## 1. Derivative Coverage
The Open Data Gateway now supports public collection for:
- NIFTY / BANKNIFTY Futures.
- Index Options (Selected ATM strikes).
- Stock Futures.

## 2. Integrity Gate
A hard rule has been implemented in the `PriceResolver`:
- Derivative prices must be retrieved from the `OPTIONS` or `FUTURES` data paths.
- Copying the `EQUITY` spot price into a derivative field is strictly rejected with a `DATA_CONTAMINATION` error.

## 3. Data Status
| Instrument | Source | Availability | Status |
| :--- | :--- | :--- | :--- |
| **NIFTY FUT** | NSE OC API | LIVE_PUBLIC | OPERATIONAL |
| **Option ATM** | NSE OC API | LIVE_PUBLIC | OPERATIONAL |

---
**Verdict**: F&O_READY.
