import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv(os.path.join("backend", ".env"))

db_url = os.getenv("POSTGRES_URL")
if db_url and db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

def check_counts():
    if not db_url:
        print("POSTGRES_URL not found")
        return

    engine = create_engine(db_url)
    try:
        with engine.connect() as conn:
            print("--- CLOUD SIGNAL COUNTS ---")
            # 1. Total Signals
            total = conn.execute(text("SELECT count(*) FROM live_signals")).scalar()
            print(f"Total Signals: {total}")

            # 2. Counts by Timeframe
            print("\nCounts by Timeframe:")
            res = conn.execute(text("SELECT timeframe, count(*) FROM live_signals GROUP BY timeframe")).fetchall()
            for row in res:
                print(f"  - {row[0]}: {row[1]}")

            # 3. Counts by Status
            print("\nCounts by Status:")
            res = conn.execute(text("SELECT status, count(*) FROM live_signals GROUP BY status")).fetchall()
            for row in res:
                print(f"  - {row[0]}: {row[1]}")

            # 4. Detailed Breakdown (Timeframe + Status)
            print("\nTimeframe + Status Breakdown:")
            res = conn.execute(text("SELECT timeframe, status, count(*) FROM live_signals GROUP BY timeframe, status")).fetchall()
            for row in res:
                print(f"  - {row[0]} | {row[1]}: {row[2]}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_counts()
