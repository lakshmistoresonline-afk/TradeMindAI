import sqlalchemy
from sqlalchemy import text
import pandas as pd
import os

def fetch():
    db_url = "postgresql://neondb_owner:npg_L5GbM3HeYfry@ep-fancy-mountain-axa35p28-pooler.c-4.us-east-2.aws.neon.tech/neondb?sslmode=require"
    engine = sqlalchemy.create_engine(db_url)

    with engine.connect() as conn:
        print("Fetching Active Signals...")
        # Active Signals
        active_query = "SELECT * FROM live_signals WHERE status NOT IN ('TARGET_HIT', 'STOP_LOSS', 'EXPIRED', 'CANCELLED', 'TIMEOUT') LIMIT 33"
        active_df = pd.read_sql_query(text(active_query), conn)

        print("Fetching Historical Signals...")
        # Historical Signals (from shadow_signals as per service logic)
        historical_query = "SELECT * FROM shadow_signals WHERE status IN ('TARGET_HIT', 'STOP_LOSS', 'EXPIRED') LIMIT 50"
        historical_df = pd.read_sql_query(text(historical_query), conn)

        print("\n--- ACTIVE SIGNALS ---")
        print(active_df[['id', 'symbol', 'direction', 'timeframe', 'entry_price', 'target_price', 'stop_price', 'status', 'calibrated_probability', 'expected_value']].to_markdown())

        print("\n--- HISTORICAL SIGNALS ---")
        print(historical_df[['id', 'symbol', 'direction', 'signal_type', 'entry_price', 'target_price', 'stop_price', 'status', 'net_pnl', 'calibrated_probability']].to_markdown())

        # Save to CSV for the report
        active_df.to_csv("active_signals.csv", index=False)
        historical_df.to_csv("historical_signals.csv", index=False)

if __name__ == "__main__":
    fetch()
