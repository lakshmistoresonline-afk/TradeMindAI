import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load backend environment variables
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend", ".env"))

from backend.core.postgres import SessionLocal, LiveSignalDB
from backend.core.database import db_client

def find_earliest():
    print("--- TRADEMIND DATA AUDIT: EARLIEST RECORDS ---")

    # 1. Postgres: Live Signals
    session = SessionLocal()
    earliest_pg = session.query(LiveSignalDB.timestamp).order_by(LiveSignalDB.timestamp.asc()).first()
    latest_pg = session.query(LiveSignalDB.timestamp).order_by(LiveSignalDB.timestamp.desc()).first()
    total_pg = session.query(LiveSignalDB).count()

    print(f"\n1. POSTGRES (Live Signals Table):")
    print(f"   - Earliest: {earliest_pg[0] if earliest_pg else 'None'}")
    print(f"   - Latest:   {latest_pg[0] if latest_pg else 'None'}")
    print(f"   - Total:    {total_pg}")

    # 2. Firestore: Backtests and Signals
    print(f"\n2. FIRESTORE (Backtests Collection):")
    earliest_fs = None
    latest_fs = None
    total_fs_signals = 0

    backtests = db_client.collection("backtests").stream()
    for bt in backtests:
        signals = db_client.collection("backtests").document(bt.id).collection("signals").stream()
        for s in signals:
            data = s.to_dict()
            date_str = data.get("date") # Usually YYYY-MM-DD
            if date_str:
                dt = datetime.strptime(date_str, "%Y-%m-%d")
                if earliest_fs is None or dt < earliest_fs:
                    earliest_fs = dt
                if latest_fs is None or dt > latest_fs:
                    latest_fs = dt
                total_fs_signals += 1

    print(f"   - Earliest Signal: {earliest_fs if earliest_fs else 'None'}")
    print(f"   - Latest Signal:   {latest_fs if latest_fs else 'None'}")
    print(f"   - Total Signals:   {total_fs_signals}")

    session.close()

if __name__ == "__main__":
    find_earliest()
