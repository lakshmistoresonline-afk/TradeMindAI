import os
import sqlalchemy
from sqlalchemy import text
from dotenv import load_dotenv
import pandas as pd

load_dotenv('backend/.env')
db_url = os.getenv('POSTGRES_URL')
engine = sqlalchemy.create_engine(db_url)

def reconcile():
    with engine.connect() as conn:
        print("=== TRADEMIND AI: FINAL RECONCILIATION 2.0 ===")

        # 1. Terminal Records (History)
        res = conn.execute(text("SELECT id, symbol, status, realized_return, outcome_timestamp FROM shadow_signals WHERE status NOT IN ('ACTIVE', 'WAITING_FOR_ENTRY', 'ENTRY_TRIGGERED')"))
        df = pd.DataFrame(res.fetchall(), columns=res.keys())

        print(f"Total Historical Records: {len(df)}")

        # 2. Outcome Analysis
        counts = df['status'].value_counts()
        print("\nOutcome Counts:")
        print(counts)

        # 3. Binary Win Rate Population (N=49 check)
        binary_pop = df[df['status'].isin(['TARGET_HIT', 'STOP_LOSS'])]
        print(f"\nBinary Resolved Population (Wins+Losses): {len(binary_pop)}")

        # 4. Timeout check
        timeouts = df[df['status'] == 'TIMEOUT']
        print(f"Timeouts: {len(timeouts)}")

        # 5. Open Signals Analysis
        res_open = conn.execute(text("SELECT id, symbol, status FROM shadow_signals WHERE status IN ('ACTIVE', 'WAITING_FOR_ENTRY', 'ENTRY_TRIGGERED')"))
        df_open = pd.DataFrame(res_open.fetchall(), columns=res_open.keys())
        print(f"\nTotal Open Signals: {len(df_open)}")
        print(df_open['status'].value_counts())

        # 6. Terminology Check (Live Signals Table)
        res_live = conn.execute(text("SELECT status, COUNT(*) FROM live_signals GROUP BY status"))
        print("\nLive Signals Status (Current UI Source):")
        for row in res_live:
            print(f"   {row[0]}: {row[1]}")

if __name__ == "__main__":
    reconcile()
