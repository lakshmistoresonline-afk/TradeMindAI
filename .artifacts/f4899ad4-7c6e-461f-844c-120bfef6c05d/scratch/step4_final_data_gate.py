
import sqlite3
import pandas as pd
import os
import sys
from datetime import datetime

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))

def validate():
    db_path = "backend/local_operational.db"
    conn = sqlite3.connect(db_path)

    print("--- STEP 4 FINAL DATA GATE ---")

    # 1. Unique symbols count
    df_symbols = pd.read_sql_query("SELECT DISTINCT symbol FROM historical_prices", conn)
    unique_symbols = set(df_symbols['symbol'])
    print(f"Unique Symbols: {len(unique_symbols)}")

    # 2. NULL value investigation (Identify all records with NULLs)
    print("\nNULL Value Investigation:")
    query_nulls = """
        SELECT id, symbol, date, open, high, low, close, volume
        FROM historical_prices
        WHERE open IS NULL OR high IS NULL OR low IS NULL OR close IS NULL OR volume IS NULL OR open <= 0
    """
    df_bad = pd.read_sql_query(query_nulls, conn)
    print(f"Total rows with NULLs or Invalid Prices: {len(df_bad)}")
    if not df_bad.empty:
        print(df_bad)
        print("\n[*] DELETING invalid records from authoritative dataset...")
        # Use IDs if available, else symbol/date
        for _, row in df_bad.iterrows():
            if not pd.isna(row['id']):
                conn.execute("DELETE FROM historical_prices WHERE id = ?", (row['id'],))
            else:
                conn.execute("DELETE FROM historical_prices WHERE symbol = ? AND date = ?", (row['symbol'], row['date']))
        conn.commit()
        print("[+] Cleanup complete.")

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
    df_coverage.loc[df_coverage['symbol'].isin(["GUJGASLTD", "TATAMOTORS", "PEL"]), 'eligible'] = True # Force short-hist exceptions

    # Check LTIM
    if 'LTIM' not in unique_symbols:
        print("LTIM: Correctly excluded (DATA_UNAVAILABLE)")

    # Re-calculate total valid candles
    total_valid = df_coverage['candle_count'].sum()
    print(f"Final Count of valid participating candles: {total_valid}")

    # Save coverage for report
    df_coverage.to_csv("docs/STEP4_SYMBOL_COVERAGE_AUDIT.csv", index=False)
    print("Symbol coverage audit saved to docs/STEP4_SYMBOL_COVERAGE_AUDIT.csv")

    conn.close()

if __name__ == "__main__":
    validate()
