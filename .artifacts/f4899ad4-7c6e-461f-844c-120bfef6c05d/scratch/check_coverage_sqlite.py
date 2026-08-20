
import sqlite3
import pandas as pd

def check():
    db_path = "backend/local_operational.db"
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query("SELECT symbol, count(*) as count FROM historical_prices GROUP BY symbol", conn)

    print(f"Total symbols with data: {len(df)}")
    print(f"Symbols with >= 1000 candles: {len(df[df['count'] >= 1000])}")
    print(f"Symbols with < 1000 candles: {len(df[df['count'] < 1000])}")

    if len(df[df['count'] < 1000]) > 0:
        print("\nLow coverage symbols (first 20):")
        print(df[df['count'] < 1000].sort_values('count').head(20))

    conn.close()

if __name__ == "__main__":
    check()
