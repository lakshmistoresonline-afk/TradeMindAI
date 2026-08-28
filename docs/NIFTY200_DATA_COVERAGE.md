# NIFTY 200 Historical Data Coverage Report

**Last Updated**: 2026-08-16
**Status**: MASTER POPULATED / CANDLE SYNC PENDING

## 1. Summary

The NIFTY 200 Universe has been canonicalized to exactly 200 unique symbols. Master records are present in the local database. Historical candle population is designated as a **Manual Local Operation** to comply with P0 infrastructure requirements.

| Metric | Value |
| :--- | :--- |
| Expected Constituents | 200 |
| Unique Constituents in DB | 200 |
| Missing Constituents | 0 |
| Duplicate Constituents | 0 |
| Data Provider | yfinance / Groww |

## 2. Coverage by Sector

| Sector | Symbol Count | Data Quality |
| :--- | :--- | :--- |
| Financial Services | 32 | PENDING |
| Energy | 15 | PENDING |
| IT | 14 | PENDING |
| Automobile | 14 | PENDING |
| Healthcare | 13 | PENDING |
| FMCG | 12 | PENDING |
| ... | ... | ... |

## 3. Data Sync Instruction

To populate historical candles for the full universe, run:
```powershell
scripts/windows/01_sync_market.ps1
```
Followed by the historical data backfill script (manual):
```bash
python -m scripts.data.sync_market_history --universe NIFTY_200 --start-date 2020-01-01
```

*Note: No candles are fabricated. DATA_UNAVAILABLE is reported for missing provider periods.*
