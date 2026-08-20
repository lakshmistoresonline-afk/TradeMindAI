
import sqlite3
import pandas as pd

def check():
    db_path = "backend/local_operational.db"
    conn = sqlite3.connect(db_path)
    symbol = 'ADANIPOWER'
    print(f"--- DATA CHECK: {symbol} ---")
    query = f"SELECT * FROM historical_prices WHERE symbol = '{symbol}' AND date >= '2021-08-01' LIMIT 50"
    df = pd.read_sql_query(query, conn)
    print(df)
    conn.close()

if __name__ == "__main__":
    check()
