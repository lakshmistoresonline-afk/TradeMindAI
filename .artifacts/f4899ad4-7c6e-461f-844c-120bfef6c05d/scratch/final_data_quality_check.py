
import sqlite3
import pandas as pd
import os

def check():
    db_path = "backend/local_operational.db"
    conn = sqlite3.connect(db_path)

    print("--- SQLITE DATA QUALITY AUDIT ---")

    # 1. Null checks
    query_nulls = """
        SELECT
            SUM(CASE WHEN open IS NULL THEN 1 ELSE 0 END) as open_null,
            SUM(CASE WHEN high IS NULL THEN 1 ELSE 0 END) as high_null,
            SUM(CASE WHEN low IS NULL THEN 1 ELSE 0 END) as low_null,
            SUM(CASE WHEN close IS NULL THEN 1 ELSE 0 END) as close_null,
            SUM(CASE WHEN volume IS NULL THEN 1 ELSE 0 END) as volume_null
        FROM historical_prices
    """
    nulls = pd.read_sql_query(query_nulls, conn).iloc[0]
    print(f"Null Values:\n{nulls}")

    # 2. Zero/Negative checks
    query_zeros = """
        SELECT
            SUM(CASE WHEN open <= 0 THEN 1 ELSE 0 END) as open_zero,
            SUM(CASE WHEN high <= 0 THEN 1 ELSE 0 END) as high_zero,
            SUM(CASE WHEN low <= 0 THEN 1 ELSE 0 END) as low_zero,
            SUM(CASE WHEN close <= 0 THEN 1 ELSE 0 END) as close_zero
        FROM historical_prices
    """
    zeros = pd.read_sql_query(query_zeros, conn).iloc[0]
    print(f"\nZero/Negative Values:\n{zeros}")

    # 3. Source check
    query_source = "SELECT DISTINCT source FROM historical_prices"
    sources = pd.read_sql_query(query_source, conn)
    print(f"\nDistinct Sources:\n{sources}")

    # 4. Sample data for GUJGASLTD
    print("\nGUJGASLTD Sample:")
    df_guj = pd.read_sql_query("SELECT * FROM historical_prices WHERE symbol = 'GUJGASLTD' LIMIT 5", conn)
    print(df_guj)

    conn.close()

if __name__ == "__main__":
    check()
