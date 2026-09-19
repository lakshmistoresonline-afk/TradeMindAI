import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime, timezone
from sqlalchemy import text

# Add project root to path
sys.path.append(os.getcwd())

# Ensure Neon connection
os.environ["ENVIRONMENT"] = "production"
os.environ["SECRET_KEY"] = "A" * 32
os.environ["MARKET_DATA_INGEST_KEY"] = "SECURE_INGEST_KEY_2026"
os.environ["POSTGRES_URL"] = "postgresql://neondb_owner:npg_L5GbM3HeYfry@ep-fancy-mountain-axa35p28-pooler.c-4.us-east-2.aws.neon.tech/neondb?sslmode=require"

from backend.core.postgres import SessionLocal

def analyze():
    db = SessionLocal()
    try:
        # We need activation_timestamp or similar
        # For shadow signals, we have 'timestamp' as generation.
        # Entry often happens at the next bar or close.
        # Let's check for 'activated_at' or 'entry_timestamp'

        cols = ["id", "symbol", "status", "timestamp", "activated_at", "entry_price", "current_price"]

        query = text(f"""
            SELECT id, symbol, status, timestamp, activated_at, entry_price, current_price
            FROM live_signals
            UNION ALL
            SELECT id, symbol, status, timestamp, entry_timestamp as activated_at, entry_price, current_price
            FROM shadow_signals
        """)
        res = db.execute(query)
        data = [dict(zip(["id", "symbol", "status", "timestamp", "activated_at", "entry_price", "current_price"], row)) for row in res.fetchall()]

        df = pd.DataFrame(data)
        resolved = df[df['status'].isin(['TARGET_HIT', 'STOP_LOSS'])].copy()

        if resolved.empty:
            print("[!] No resolved signals for timing analysis.")
            return

        resolved['timestamp'] = pd.to_datetime(resolved['timestamp'])
        resolved['activated_at'] = pd.to_datetime(resolved['activated_at'])

        # Entry Delay in Hours
        resolved['entry_delay_hrs'] = (resolved['activated_at'] - resolved['timestamp']).dt.total_seconds() / 3600.0

        print("[*] Entry Timing Analysis...")
        resolved['delay_bin'] = pd.cut(resolved['entry_delay_hrs'], bins=[-1, 0, 1, 2, 4, 8, 24, 1000])
        delay_perf = resolved.groupby('delay_bin', observed=False).agg(
            count=('id', 'count'),
            win_rate=('status', lambda x: (x == 'TARGET_HIT').mean() * 100)
        )
        print(delay_perf)

        with open("reports/ENTRY_TIMING_ANALYSIS.md", "w") as f:
            f.write("# Entry Timing Analysis\n\n")
            f.write("## Entry Delay vs Win Rate\n")
            f.write(delay_perf.to_markdown())

        print("\n[SUCCESS] Entry timing report saved.")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    analyze()
