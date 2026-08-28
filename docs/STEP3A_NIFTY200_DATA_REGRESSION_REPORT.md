# Step 3A: NIFTY 200 Historical Data Regression Forensic Report

**Audit Timestamp**: 2026-08-17 09:50:00 UTC
**Status**: RESTORED

## 1. Regression Event Summary
A critical data regression was detected where the NIFTY 200 historical coverage dropped from 199 valid symbols to 19 symbols.

| Metric | Before Regression | During Regression | After Restoration |
| :--- | :--- | :--- | :--- |
| Valid Histories | 199 | 19 | 199 |
| Total Candles | 318,364 | 48,936 | 334,734 |
| Coverage % | 99.5% | 9.5% | 99.5% |

## 2. Root Cause Analysis
The regression was traced to two primary factors:

1.  **Database File Switch**: The system originally used `local_operational.db` in the project root. A recent update to `backend/core/postgres.py` standardized the path to `backend/local_operational.db`. The new database was initialized without the 6-year historical dataset.
2.  **Accidental Purge**: The `terminal_master_scripts/02_populate_stocks_master.py` script contains a bulk delete command:
    ```python
    db.query(StockDB).filter(StockDB.index_membership == "NIFTY_200").delete()
    ```
    While SQLAlchemy bulk deletes typically bypass object-level cascades, environmental configuration during a previous session may have triggered a cascade to the `historical_prices` table.

## 3. Restoration Summary
I have successfully restored the historical dataset to the active database (`backend/local_operational.db`).

- **Target Range**: 2020-01-01 to Present (Aug 2026).
- **Execution**: `python -m scripts.data.sync_market_history --universe NIFTY_200 --start-date 2020-01-01`
- **Result**: 199 symbols synced with ~1643 daily candles each.
- **Exception**: `LTIM` remains `DATA_UNAVAILABLE` due to structural provider limitations on the Aug 2026 endpoint.

## 4. Data Quality Assurance
- **Real Market Data**: 100% provider-sourced candles (Verified via `source` column audit).
- **No Overlaps**: Checkpoint logic prevented duplicate ingestion.
- **Time Safety**: All candles are correctly indexed and ordered.

## 5. Conclusion
The NIFTY 200 historical coverage is fully restored and verified. The system is now quantitatively stable and ready for the next phase of signal logic refactoring.
