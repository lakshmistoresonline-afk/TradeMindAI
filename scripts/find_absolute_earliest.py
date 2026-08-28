import os
import sys
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load backend environment variables
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend", ".env"))

from backend.core.postgres import SessionLocal, PriceDB, LiveSignalDB, RegimeDB
from backend.core.database import db_client

def find():
    print("--- TRADEMIND AI: ABSOLUTE DATA HISTORY START DATE ---")
    session = SessionLocal()

    earliest_price = session.query(PriceDB.date).order_by(PriceDB.date.asc()).first()
    earliest_signal = session.query(LiveSignalDB.timestamp).order_by(LiveSignalDB.timestamp.asc()).first()
    earliest_regime = session.query(RegimeDB.date).order_by(RegimeDB.date.asc()).first()

    print(f"\n1. POSTGRES DATA:")
    print(f"   - Earliest Historical Price: {earliest_price[0] if earliest_price else 'None'}")
    print(f"   - Earliest Live Signal:     {earliest_signal[0] if earliest_signal else 'None'}")
    print(f"   - Earliest Market Regime:    {earliest_regime[0] if earliest_regime else 'None'}")

    # Check Firestore
    backtests = db_client.collection("backtests").stream()
    earliest_bt = None
    for bt in backtests:
        sigs = db_client.collection("backtests").document(bt.id).collection("signals").order_by("date").limit(1).get()
        for s in sigs:
            d = s.to_dict().get('date')
            if d and (earliest_bt is None or d < earliest_bt): earliest_bt = d

    print(f"\n2. FIRESTORE DATA:")
    print(f"   - Earliest Model Signal:    {earliest_bt if earliest_bt else 'None'}")

    session.close()

if __name__ == "__main__":
    find()
