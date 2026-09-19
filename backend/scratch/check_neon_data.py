import os
import sys
from dotenv import load_dotenv
from sqlalchemy import text

# Add project root to path
sys.path.append(os.getcwd())

# Load environment variables
load_dotenv('backend/.env')

from backend.core.postgres import SessionLocal, DATABASE_URL

def check():
    print(f"Active DATABASE_URL: {DATABASE_URL}")
    db = SessionLocal()
    try:
        # 1. Count signals
        shadow_count = db.execute(text("SELECT count(*) FROM shadow_signals")).scalar()
        live_count = db.execute(text("SELECT count(*) FROM live_signals")).scalar()

        print(f"Shadow Signals: {shadow_count}")
        print(f"Live Signals: {live_count}")

        # 2. Status distribution for all non-ACTIVE signals
        statuses = db.execute(text("""
            SELECT status, count(*)
            FROM (
                SELECT status FROM shadow_signals WHERE status != 'ACTIVE'
                UNION ALL
                SELECT status FROM live_signals WHERE status != 'ACTIVE'
            ) as combined
            GROUP BY status
        """)).fetchall()

        print("\nResolved Outcomes (Terminal States):")
        for status, count in statuses:
            print(f"  {status}: {count}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check()
