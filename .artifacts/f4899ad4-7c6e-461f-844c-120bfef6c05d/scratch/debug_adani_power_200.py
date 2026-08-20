
import sqlite3
import pandas as pd

def check():
    db_path = "backend/local_operational.db"
    conn = sqlite3.connect(db_path)
    symbol = 'ADANIPOWER'
    print(f"--- DATA CHECK: {symbol} 200 bars later ---")
    query = f"SELECT date, close FROM historical_prices WHERE symbol = '{symbol}' AND date >= '2021-08-24' ORDER BY date LIMIT 210"
    df = pd.read_sql_query(query, conn)
    print(df.iloc[[0, 10, 50, 100, 150, 199, 200, 201]])
    conn.close()

if __name__ == "__main__":
    check()
