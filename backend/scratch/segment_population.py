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

def segment():
    db = SessionLocal()
    try:
        query = text("""
            SELECT id, symbol, status, entry_price, stop_price, target_price, risk_reward_ratio, strategy_version, timestamp, created_at, evaluation_mode
            FROM shadow_signals
            WHERE strategy_version = 'v2.2'
            UNION ALL
            SELECT id, symbol, status, entry_price, stop_price, target_price, risk_reward_ratio, strategy_version, timestamp, created_at, evaluation_mode
            FROM live_signals
            WHERE strategy_version = 'v2.2'
        """)
        res = db.execute(query)
        df = pd.DataFrame([dict(row._mapping) for row in res.fetchall()])

        if df.empty:
            print("[!] No signals found.")
            return

        # Calculate Stop/Target Distance %
        df['stop_dist_pct'] = (abs(df['entry_price'] - df['stop_price']) / df['entry_price'] * 100).round(2)
        df['target_dist_pct'] = (abs(df['target_price'] - df['entry_price']) / df['entry_price'] * 100).round(2)
        df['calc_rr'] = (df['target_dist_pct'] / df['stop_dist_pct']).round(2)

        print(f"[*] Analyzing {len(df)} V2.2 signals.")

        # Segment by Evaluation Mode and Risk Geometry
        # Identify common geometries
        df['geometry'] = df.apply(lambda r: f"S:{r['stop_dist_pct']}% / T:{r['target_dist_pct']}% (RR:{r['calc_rr']})", axis=1)

        segmentation = df.groupby(['evaluation_mode', 'geometry']).size().reset_index(name='count')
        print("\nPopulation Segmentation (Mode + Geometry):")
        print(segmentation)

        # Status distribution by geometry
        print("\nStatus Distribution by Geometry:")
        status_geom = df.groupby(['geometry', 'status']).size().unstack(fill_value=0)
        print(status_geom)

    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    segment()
