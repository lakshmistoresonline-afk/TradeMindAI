import sqlite3
import pandas as pd
import os

def inspect():
    db_path = "backend/local_operational.db"
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query("SELECT status, count(*) FROM live_signals GROUP BY status", conn)
    print(df)

    # Get 50 closed signals from live_signals if they exist
    closed_df = pd.read_sql_query("SELECT * FROM live_signals WHERE status IN ('TARGET_HIT', 'STOP_LOSS', 'EXPIRED') LIMIT 50", conn)
    print(f"\nClosed Signals in live_signals: {len(closed_df)}")
    if not closed_df.empty:
        print(closed_df[['id', 'symbol', 'status', 'net_pnl']].to_markdown())

    conn.close()

if __name__ == "__main__":
    inspect()
