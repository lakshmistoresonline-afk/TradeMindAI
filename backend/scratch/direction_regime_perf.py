import os
import sys
import pandas as pd
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
        query = text("""
            SELECT id, direction, regime, status
            FROM (
                SELECT id, direction, regime, status FROM shadow_signals WHERE status IN ('TARGET_HIT', 'STOP_LOSS')
                UNION ALL
                SELECT id, direction, regime, status FROM live_signals WHERE status IN ('TARGET_HIT', 'STOP_LOSS')
            ) as combined
        """)
        res = db.execute(query)
        df = pd.DataFrame([dict(zip(['id', 'direction', 'regime', 'status'], row)) for row in res.fetchall()])

        if df.empty:
            print("[!] No data.")
            return

        print("[*] Directional Performance by Regime...")
        perf = df.groupby(['regime', 'direction'], observed=False).agg(
            count=('id', 'count'),
            win_rate=('status', lambda x: (x == 'TARGET_HIT').mean() * 100)
        )
        print(perf)

    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    analyze()
