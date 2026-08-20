
import os
import sys
import sqlite3
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')

def reconcile():
    # 1. Get SQLite stats
    db_path = "backend/local_operational.db"
    conn_sq = sqlite3.connect(db_path)
    df_sq = pd.read_sql_query("SELECT symbol, count(*) as sq_count, min(date) as sq_start, max(date) as sq_end FROM historical_prices GROUP BY symbol", conn_sq)
    conn_sq.close()

    # 2. Get Neon stats (Unique only)
    pg_url = os.getenv("POSTGRES_URL")
    engine = create_engine(pg_url)
    with engine.connect() as conn_pg:
        query = text("""
            SELECT symbol, count(*) as pg_count, min(date) as pg_start, max(date) as pg_end
            FROM (SELECT DISTINCT symbol, date FROM historical_prices) as t
            GROUP BY symbol
        """)
        df_pg = pd.read_sql_query(query, conn_pg)

    # 3. Analysis
    # Total unique Neon candles = 338,278 (based on user's numbers)
    # Total unique SQLite candles = 334,682

    merged = pd.merge(df_sq, df_pg, on='symbol', how='outer', suffixes=('_sq', '_pg'))

    # Symbols in Neon but NOT in SQLite
    neon_only = merged[merged['sq_count'].isna()]
    print("--- SYMBOLS ONLY IN NEON ---")
    print(neon_only[['symbol', 'pg_count', 'pg_start', 'pg_end']])

    # Overlapping symbols where Neon has MORE data
    more_in_neon = merged[(merged['sq_count'] < merged['pg_count'])]
    print("\n--- OVERLAPPING SYMBOLS WITH MORE DATA IN NEON ---")
    print(more_in_neon[['symbol', 'sq_count', 'pg_count', 'sq_start', 'pg_start']].head(10))

    # Overlapping symbols where SQLite has MORE data
    more_in_sq = merged[(merged['sq_count'] > merged['pg_count'])]
    print("\n--- OVERLAPPING SYMBOLS WITH MORE DATA IN SQLITE ---")
    print(more_in_sq[['symbol', 'sq_count', 'pg_count', 'sq_end', 'pg_end']].head(10))

if __name__ == "__main__":
    reconcile()
