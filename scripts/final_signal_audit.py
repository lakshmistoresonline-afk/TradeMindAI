import os
import sys
from datetime import datetime
from dotenv import load_dotenv
from collections import Counter

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load backend environment variables
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend", ".env"))

from backend.core.postgres import SessionLocal, LiveSignalDB
from backend.core.database import db_client

def audit():
    print("--- TRADEMIND AI: FINAL SIGNAL AUDIT ---")
    session = SessionLocal()

    # 1. Live Signals (Postgres)
    live = session.query(LiveSignalDB).all()

    # 2. Backtest Signals (Firestore)
    bt_signals = []
    backtests = db_client.collection("backtests").stream()
    for bt in backtests:
        signals = db_client.collection("backtests").document(bt.id).collection("signals").stream()
        for s in signals:
            bt_signals.append(s.to_dict())

    total_count = len(live) + len(bt_signals)

    def get_tf(s):
        if hasattr(s, 'timeframe'): return s.timeframe
        return s.get('timeframe', 'SWING')

    def get_status(s):
        if hasattr(s, 'status'): return s.status
        return s.get('outcome', 'UNKNOWN')

    tfs = [get_tf(s) for s in live] + [get_tf(s) for s in bt_signals]
    statuses = [get_status(s) for s in live] + [get_status(s) for s in bt_signals]

    print(f"\n1. Total Signals: {total_count}")
    print(f"   Breakdown by Timeframe: {dict(Counter(tfs))}")
    print(f"   Breakdown by Outcome:   {dict(Counter(statuses))}")

    # Target Achievement Rate
    resolved = [s for s in live if s.status != "ACTIVE"] + [s for s in bt_signals if s.get('outcome') != "ACTIVE"]
    wins = [s for s in resolved if (hasattr(s, 'status') and s.status == "TARGET_HIT") or (isinstance(s, dict) and s.get('outcome') == "TARGET_HIT")]

    if resolved:
        win_rate = (len(wins) / len(resolved)) * 100
        print(f"\n2. Performance Metrics:")
        print(f"   Resolved Signals: {len(resolved)}")
        print(f"   Win Rate:         {win_rate:.1f}%")

    # Earliest Date
    earliest_pg = session.query(LiveSignalDB.timestamp).order_by(LiveSignalDB.timestamp.asc()).first()
    earliest_fs = None
    for s in bt_signals:
        d = s.get('date')
        if d:
            dt = datetime.strptime(d, "%Y-%m-%d")
            if earliest_fs is None or dt < earliest_fs: earliest_fs = dt

    print(f"\n3. Earliest Records:")
    print(f"   Postgres:  {earliest_pg[0] if earliest_pg else 'None'}")
    print(f"   Firestore: {earliest_fs if earliest_fs else 'None'}")

    session.close()

if __name__ == "__main__":
    audit()
