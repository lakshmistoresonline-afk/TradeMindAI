
import os
import sys
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')

def verify_integrity(engine, label):
    print(f"\n--- VERIFYING INTEGRITY: {label} ---")
    with engine.connect() as conn:
        # 1. Candle count
        count = conn.execute(text("SELECT count(*) FROM historical_prices")).scalar()
        print(f"Total Candles: {count}")

        # 2. Unique Symbols
        symbols = conn.execute(text("SELECT distinct symbol FROM historical_prices")).fetchall()
        symbols = [s[0] for s in symbols]
        print(f"Unique Symbols: {len(symbols)}")

        # 3. LTIM exclusion
        print(f"LTIM in data: {'LTIM' in symbols}")

        # 4. Duplicates
        dup_count = conn.execute(text("SELECT count(*) FROM (SELECT symbol, date, count(*) FROM historical_prices GROUP BY symbol, date HAVING count(*) > 1) as t")).scalar()
        print(f"Duplicate Candles: {dup_count}")

        # 5. Synthetic Data Check (Source check)
        try:
            sources = conn.execute(text("SELECT distinct source FROM historical_prices")).fetchall()
            print(f"Sources: {[s[0] for s in sources]}")
        except Exception as e:
            print(f"Could not check sources: {e}")

def main():
    pg_url = os.getenv("POSTGRES_URL")
    if pg_url:
        verify_integrity(create_engine(pg_url), "Neon PostgreSQL")

    import sqlite3
    sqlite_path = "backend/local_operational.db"
    if os.path.exists(sqlite_path):
        verify_integrity(create_engine(f"sqlite:///{sqlite_path}"), "Local SQLite")

if __name__ == "__main__":
    main()
