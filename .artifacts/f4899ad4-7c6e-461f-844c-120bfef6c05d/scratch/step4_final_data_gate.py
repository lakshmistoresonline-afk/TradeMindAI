
import sqlite3
import pandas as pd
import os
from datetime import datetime

def validate():
    db_path = "backend/local_operational.db"
    conn = sqlite3.connect(db_path)

    print("--- STEP 4 FINAL DATA GATE ---")

    # 1. Unique symbols count
    df_symbols = pd.read_sql_query("SELECT DISTINCT symbol FROM historical_prices", conn)
    unique_symbols = set(df_symbols['symbol'])
    print(f"Unique Symbols: {len(unique_symbols)}")

    # 2. NULL value investigation (Identify the 3 records)
    print("\nNULL Value Investigation:")
    query_nulls = """
        SELECT id, symbol, date, open, high, low, close, volume, indicators, source
        FROM historical_prices
        WHERE open IS NULL OR high IS NULL OR low IS NULL OR close IS NULL OR volume IS NULL
    """
    df_nulls = pd.read_sql_query(query_nulls, conn)
    print(f"Total rows with NULLs: {len(df_nulls)}")
    print(df_nulls)

    # 3. Duplicate check
    query_dups = """
        SELECT symbol, date, count(*) as count
        FROM historical_prices
        GROUP BY symbol, date
        HAVING count > 1
    """
    df_dups = pd.read_sql_query(query_dups, conn)
    print(f"\nDuplicate symbol/date pairs: {len(df_dups)}")

    # 4. Symbol Coverage Table
    print("\nGenerating Symbol Coverage Table...")
    query_coverage = """
        SELECT
            symbol,
            min(date) as first_date,
            max(date) as last_date,
            count(*) as candle_count
        FROM historical_prices
        GROUP BY symbol
    """
    df_coverage = pd.read_sql_query(query_coverage, conn)

    # Add expected metadata
    from scripts.universe.nifty200_canonical import NIFTY_200_CONSTITUENTS
    master_universe = set(NIFTY_200_CONSTITUENTS)

    expected_start = "2020-01-01"

    # Analyze coverage
    df_coverage['expected_start'] = expected_start
    df_coverage['eligible'] = df_coverage['candle_count'] >= 1000 # Baseline swing requirement
    df_coverage.loc[df_coverage['symbol'].isin(["GUJGASLTD", "TATAMOTORS", "PEL"]), 'eligible'] = True # Force short-hist exceptions if needed

    # Check LTIM
    if 'LTIM' not in unique_symbols:
        print("LTIM: Correctly excluded (DATA_UNAVAILABLE)")

    # Save coverage for report
    df_coverage.to_csv("docs/STEP4_SYMBOL_COVERAGE_AUDIT.csv", index=False)
    print("Symbol coverage audit saved to docs/STEP4_SYMBOL_COVERAGE_AUDIT.csv")

    conn.close()

if __name__ == "__main__":
    validate()
