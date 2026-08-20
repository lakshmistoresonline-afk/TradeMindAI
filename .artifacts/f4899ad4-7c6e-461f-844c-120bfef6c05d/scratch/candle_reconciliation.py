
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

    # 3. Merge for comparison
    df_merged = pd.merge(df_sq, df_pg, on='symbol', how='outer')
    df_merged['diff'] = df_merged['pg_count'].fillna(0) - df_merged['sq_count'].fillna(0)

    print("--- CANDLE RECONCILIATION SUMMARY ---")
    print(f"Symbols in SQLite: {len(df_sq)}")
    print(f"Symbols in Neon: {len(df_pg)}")

    # Symbols in Neon but not in SQLite?
    neon_only = df_merged[df_merged['sq_count'].isna()]
    print(f"Symbols ONLY in Neon: {len(neon_only)}")
    if not neon_only.empty:
        print(neon_only[['symbol', 'pg_count']])

    # Difference in overlapping symbols
    overlapping = df_merged.dropna(subset=['sq_count', 'pg_count'])
    print(f"Overlapping symbols: {len(overlapping)}")

    total_diff = df_merged['diff'].sum()
    print(f"Total Unique Candle Difference (Neon - SQLite): {total_diff}")

    # Top differences
    print("\nTop Symbol-level Differences:")
    print(df_merged.sort_values('diff', ascending=False).head(10)[['symbol', 'sq_count', 'pg_count', 'diff', 'sq_start', 'pg_start']])

if __name__ == "__main__":
    reconcile()
