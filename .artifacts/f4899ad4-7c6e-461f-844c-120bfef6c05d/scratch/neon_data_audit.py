
import os
import sys
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')

def audit():
    pg_url = os.getenv("POSTGRES_URL")
    if not pg_url:
        print("POSTGRES_URL not found")
        return

    engine = create_engine(pg_url)

    with engine.connect() as conn:
        print("--- NEON POSTGRESQL AUDIT ---")

        # 1. Database Info
        res = conn.execute(text("SELECT current_database(), current_user, inet_server_addr()")).fetchone()
        print(f"Database: {res[0]} | User: {res[1]} | Server: {res[2]}")

        # 2. Shadow Signals
        signals_df = pd.read_sql_query("SELECT id, symbol, status, net_return, timestamp FROM shadow_signals", conn)
        print(f"\nShadow Signals Count: {len(signals_df)}")
        print(signals_df)

        # 3. Shadow Events
        events_count = conn.execute(text("SELECT count(*) FROM shadow_events")).scalar()
        print(f"\nShadow Events Count: {events_count}")

        # 4. Baseline check
        baseline_start = '2026-08-18'
        baseline_signals = conn.execute(text(f"SELECT count(*) FROM shadow_signals WHERE timestamp >= '{baseline_start}'")).scalar()
        print(f"Phase 5G Baseline Signals (>= {baseline_start}): {baseline_signals}")

if __name__ == "__main__":
    audit()
