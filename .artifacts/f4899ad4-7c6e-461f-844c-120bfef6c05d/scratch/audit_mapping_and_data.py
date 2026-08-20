
import os
import sys
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')

from backend.core.container import container
from scripts.universe.nifty200_canonical import NIFTY_200_CONSTITUENTS

def audit():
    provider = container.provider
    mapping_failures = []

    print("--- PROVIDER MAPPING AUDIT ---")
    for s in NIFTY_200_CONSTITUENTS:
        try:
            mapped = provider._map_symbol(s)
            # print(f"{s} -> {mapped}")
        except Exception as e:
            mapping_failures.append(s)

    print(f"Total Mapping Failures: {len(mapping_failures)}")
    if mapping_failures:
        print(f"Failed symbols: {mapping_failures[:10]}...")

    print("\n--- DATASET RECONCILIATION ---")
    import sqlite3
    db_path = "backend/local_operational.db"
    conn = sqlite3.connect(db_path)

    # Symbols with data
    df_counts = pd.read_sql_query("SELECT symbol, count(*) as rows FROM historical_prices GROUP BY symbol", conn)
    symbols_with_data = set(df_counts['symbol'])

    print(f"Unique symbols in SQLite with data: {len(symbols_with_data)}")

    master_set = set(NIFTY_200_CONSTITUENTS)
    missing_from_master = master_set - symbols_with_data
    extra_in_db = symbols_with_data - master_set

    print(f"Symbols in NIFTY 200 but missing data: {len(missing_from_master)}")
    if missing_from_master:
        print(f"Missing (first 10): {sorted(list(missing_from_master))[:10]}...")

    print(f"Extra symbols in DB (not in NIFTY 200): {len(extra_in_db)}")
    if extra_in_db:
        print(f"Extra (first 10): {sorted(list(extra_in_db))[:10]}...")

    total_candles = df_counts['rows'].sum()
    print(f"Total unique candles (SQLite): {total_candles}")

    conn.close()

if __name__ == "__main__":
    audit()
