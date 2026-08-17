# Step 3A: NIFTY 200 Historical Data Restoration

This plan addresses the critical data regression where only 21/200 NIFTY 200 constituents have valid history in the local database.

## User Review Required

> [!IMPORTANT]
> **Data Regression Root Cause**: The audit confirms that the local database `backend/local_operational.db` was either initialized fresh or purged during the stock master population stage. While 199 symbols have derived features in Parquet format, the raw OHLC data in the SQLite database is missing for 179 symbols.

> [!WARNING]
> **Restoration Action**: I will perform a full restoration by re-running the historical sync from **January 1, 2020**, for all 200 symbols. This will restore the previously verified 318,364 rows.

## Proposed Changes

### 1. Data Restoration
#### [SYNC] NIFTY 200 Historical Ingestion
- Run `python -m scripts.data.sync_market_history --universe NIFTY_200 --start-date 2020-01-01 --resume`
- This will use the existing checkpoint logic to fill missing symbols while skipping the 21 already present.

### 2. Forensic Report
#### [NEW] [STEP3A_NIFTY200_DATA_REGRESSION_REPORT.md](file:///G:/TradeMindAI-main/TradeMindAI-main/docs/STEP3A_NIFTY200_DATA_REGRESSION_REPORT.md)
- Document the regression event, the database switch findings, and the successful restoration of the 318k row state.

### 3. Pipeline Safeguard
#### [MODIFY] [validate_historical.py](file:///G:/TradeMindAI-main/TradeMindAI-main/scripts/universe/validate_historical.py)
- Ensure the validator explicitly prints the `DATABASE_URL` it is checking to prevent future cross-database confusion.

---

## Verification Plan

### Automated Tests
- `python -m scripts.universe.validate_historical`: Must return **PASS** with 199/200 valid histories.
- Independent SQL Check: `SELECT count(*) FROM historical_prices` must be > 300,000.

### Manual Verification
- Inspect `docs/NIFTY200_HISTORICAL_COVERAGE_REPORT.md` to ensure deep history (2020+) is reflected for all major symbols.
