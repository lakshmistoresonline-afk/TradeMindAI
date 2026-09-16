import os
import sqlalchemy
from sqlalchemy import text
from dotenv import load_dotenv

load_dotenv('backend/.env')
db_url = os.getenv('POSTGRES_URL')
engine = sqlalchemy.create_engine(db_url)

def check():
    with engine.connect() as conn:
        print("--- FINAL POPULATION RECONCILIATION ---")

        predictions = conn.execute(text("SELECT COUNT(*) FROM predictions")).scalar()
        print(f"PREDICTIONS = {predictions}")

        internal_signals = conn.execute(text("SELECT COUNT(*) FROM (SELECT id FROM live_signals UNION ALL SELECT id FROM shadow_signals) as all_sigs")).scalar()
        print(f"INTERNAL_SIGNALS = {internal_signals}")

        active = conn.execute(text("SELECT COUNT(*) FROM live_signals")).scalar()
        print(f"ACTIVE = {active}")

        historical = conn.execute(text("SELECT COUNT(*) FROM shadow_signals WHERE status != 'ACTIVE'")).scalar()
        print(f"HISTORICAL = {historical}")

        resolved = conn.execute(text("SELECT COUNT(*) FROM shadow_signals WHERE status IN ('TARGET_HIT', 'STOP_LOSS', 'TIMEOUT', 'EXPIRED')")).scalar()
        print(f"RESOLVED = {resolved}")

        print("\n--- STATUS BREAKDOWN (Historical) ---")
        res = conn.execute(text("SELECT status, COUNT(*) FROM shadow_signals WHERE status != 'ACTIVE' GROUP BY status"))
        for row in res:
            print(f"   {row[0]}: {row[1]}")

if __name__ == "__main__":
    check()
