# Task Checklist - STEP 4: Full Realized Backtest

- `[x]` Data Integrity Restoration
    - `[x]` Deduplicate local SQLite `historical_prices` table
    - `[x]` Verify 199 eligible symbols
- `[x]` Backtest Execution
    - `[x]` Implement `run_step4_backtest.py`
    - `[x]` Execute backtest against 199 symbols (38,636 trades)
    - `[x]` Aggregate metrics (Win Rate, Expectancy, R:R)
- `[x]` Reporting & Final Audit
    - `[x]` Generate `docs/STEP4_FULL_REALIZED_BACKTEST_REPORT.md`
    - `[x]` Perform regression check against known trades (SBIN)
    - `[x]` Reconcile candle counts between Neon and SQLite
