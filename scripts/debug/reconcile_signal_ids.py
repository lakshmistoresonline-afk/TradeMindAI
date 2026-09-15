import os
import sqlalchemy
from sqlalchemy import text
from dotenv import load_dotenv

load_dotenv('backend/.env')
db_url = os.getenv('POSTGRES_URL')
engine = sqlalchemy.create_engine(db_url)

def reconcile():
    with engine.connect() as conn:
        print("--- ID RECONCILIATION ---")

        # 1. Fetch all IDs from live_signals
        res_live = conn.execute(text("SELECT id FROM live_signals"))
        live_ids = set([row[0] for row in res_live])
        print(f"Live Signals (Active): {len(live_ids)}")

        # 2. Fetch all IDs from shadow_signals
        res_shadow = conn.execute(text("SELECT id FROM shadow_signals"))
        shadow_ids = set([row[0] for row in res_shadow])
        print(f"Shadow Signals (Total): {len(shadow_ids)}")

        # 3. Intersection
        overlap = live_ids.intersection(shadow_ids)
        print(f"Overlap (IDs in both): {len(overlap)}")
        if overlap:
            print(f"   Sample overlap: {list(overlap)[:5]}")

        # 4. Total History (non-ACTIVE in shadow)
        res_hist = conn.execute(text("SELECT id FROM shadow_signals WHERE status != 'ACTIVE'"))
        hist_ids = set([row[0] for row in res_hist])
        print(f"Historical Signals (Closed in shadow): {len(hist_ids)}")

        # 5. Combined Total
        all_ids = live_ids.union(shadow_ids)
        print(f"Total Unique Signal IDs: {len(all_ids)}")

if __name__ == "__main__":
    reconcile()
