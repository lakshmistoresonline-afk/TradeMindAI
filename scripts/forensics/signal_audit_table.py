import sqlite3
import pandas as pd

db_path = "backend/local_operational.db"

def generate_signal_table():
    conn = sqlite3.connect(db_path)

    query = """
    SELECT timeframe as Horizon,
           direction as Direction,
           COUNT(*) as Count
    FROM live_signals
    GROUP BY timeframe, direction
    """
    df = pd.read_sql_query(query, conn)
    pivot = df.pivot(index='Horizon', columns='Direction', values='Count').fillna(0)
    print("=== SIGNAL DISTRIBUTION TABLE ===")
    print(pivot.to_string())

    # Check for duplicates
    query = "SELECT symbol, timeframe, direction, timestamp, COUNT(*) as dups FROM live_signals GROUP BY symbol, timeframe, direction, timestamp HAVING dups > 1"
    dups = pd.read_sql_query(query, conn)
    print(f"\nDuplicate signals found: {len(dups)}")

    # Check for future timestamps
    query = "SELECT COUNT(*) FROM live_signals WHERE timestamp > datetime('now')"
    future = pd.read_sql_query(query, conn).iloc[0,0]
    print(f"Signals with future timestamps: {future}")

    conn.close()

if __name__ == "__main__":
    generate_signal_table()
