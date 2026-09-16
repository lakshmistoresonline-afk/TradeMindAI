import os
import sqlalchemy
from sqlalchemy import text
from dotenv import load_dotenv

load_dotenv('backend/.env')
db_url = os.getenv('POSTGRES_URL')
engine = sqlalchemy.create_engine(db_url)

def audit():
    with engine.connect() as conn:
        print("--- 100% TIMESTAMP INTEGRITY AUDIT ---")

        # Check all signals in both ledgers
        sql = """
        SELECT id, symbol, timestamp, data_timestamp, created_at, status
        FROM (
            SELECT id, symbol, timestamp, data_timestamp, created_at, status FROM live_signals
            UNION ALL
            SELECT id, symbol, timestamp, data_timestamp, created_at, status FROM shadow_signals
        ) as all_sigs
        """
        res = conn.execute(text(sql))
        violations = 0
        total = 0

        for row in res:
            total += 1
            sid, sym, ts, data_ts, created, status = row
            # Rule: Data <= Decision (ts)
            if data_ts and ts and data_ts > ts:
                violations += 1
                print(f"VIOLATION: {sid} ({sym}) - Data: {data_ts} > Decision: {ts}")

        print(f"\nTotal Signals Audited: {total}")
        print(f"Total Temporal Violations: {violations}")
        if total > 0:
            print(f"Integrity Rate: {(total-violations)/total:.1%}")

if __name__ == "__main__":
    audit()
