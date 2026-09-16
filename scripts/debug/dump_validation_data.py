import sqlite3
import json
import os
import pandas as pd

def dump_data():
    db_path = "backend/local_operational.db"
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return

    conn = sqlite3.connect(db_path)

    # Active Signals (33 expected)
    active_query = "SELECT * FROM live_signals WHERE status NOT IN ('TARGET_HIT', 'STOP_LOSS', 'EXPIRED', 'CANCELLED', 'TIMEOUT') LIMIT 33"
    active_df = pd.read_sql_query(active_query, conn)

    # Historical Signals (50 expected)
    historical_query = "SELECT * FROM shadow_signals"
    historical_df = pd.read_sql_query(historical_query, conn)

    print(f"\n--- SHADOW SIGNALS SUMMARY ---")
    print(f"Total Rows: {len(historical_df)}")
    if not historical_df.empty:
        print(historical_df['status'].value_counts())
        print(historical_df[['id', 'symbol', 'direction', 'signal_type', 'status', 'net_pnl']].head(50).to_markdown())

    conn.close()

if __name__ == "__main__":
    dump_data()
