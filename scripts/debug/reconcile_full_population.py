import os
import sqlalchemy
from sqlalchemy import text
from dotenv import load_dotenv

load_dotenv('backend/.env')
db_url = os.getenv('POSTGRES_URL')
engine = sqlalchemy.create_engine(db_url)

def reconcile():
    with engine.connect() as conn:
        print("--- SIGNAL POPULATION RECONCILIATION ---")

        # 1. Predictions
        res_pred = conn.execute(text("SELECT COUNT(*) FROM predictions"))
        print(f"Total Predictions: {res_pred.scalar()}")

        # 2. Live Signals (Active)
        res_live = conn.execute(text("SELECT COUNT(*) FROM live_signals"))
        print(f"Active Signals (live_signals): {res_live.scalar()}")

        # 3. Shadow Signals (Historical/Closed)
        res_shadow_closed = conn.execute(text("SELECT COUNT(*) FROM shadow_signals WHERE status != 'ACTIVE'"))
        print(f"Closed Signals (shadow_signals): {res_shadow_closed.scalar()}")

        # 4. Total Signals in Ledgers
        res_all_sig = conn.execute(text("SELECT COUNT(*) FROM (SELECT id FROM live_signals UNION ALL SELECT id FROM shadow_signals) as all_sigs"))
        print(f"Total Records in Signal Ledgers: {res_all_sig.scalar()}")

        # 5. Outcome Breakdown
        res_outcomes = conn.execute(text("SELECT status, COUNT(*) FROM shadow_signals WHERE status != 'ACTIVE' GROUP BY status"))
        print("\nHistorical Outcome Distribution:")
        for row in res_outcomes:
            print(f"   {row[0]}: {row[1]}")

        # 6. Duplicates check
        res_dupes = conn.execute(text("SELECT id, COUNT(*) FROM (SELECT id FROM live_signals UNION ALL SELECT id FROM shadow_signals) as all_sigs GROUP BY id HAVING COUNT(*) > 1"))
        dupes = res_dupes.fetchall()
        print(f"\nDuplicate Signal IDs: {len(dupes)}")

        # 7. Orphan check (Shadow signals without predictions)
        # Assuming prediction_id is the link
        res_orphans = conn.execute(text("SELECT COUNT(*) FROM shadow_signals WHERE prediction_id IS NOT NULL AND prediction_id NOT IN (SELECT id FROM predictions)"))
        print(f"Orphan Signals (No Prediction record): {res_orphans.scalar()}")

if __name__ == "__main__":
    reconcile()
