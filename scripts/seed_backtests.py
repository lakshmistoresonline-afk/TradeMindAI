import os
import sys
import datetime
from google.cloud import firestore
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load backend environment variables
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend", ".env"))

from backend.core.database import db_client

def seed():
    print("[*] Seeding Backtest Audit Data...")

    symbols = ["RELIANCE", "TCS", "HDFCBANK", "INFY", "ICICIBANK"]

    for symbol in symbols:
        # 1. Main Backtest Doc
        bt_ref = db_client.collection("backtests").document(symbol)
        bt_ref.set({
            "symbol": symbol,
            "total_return": 15.4,
            "win_rate": 68.2,
            "profit_factor": 2.1,
            "updated_at": datetime.datetime.utcnow()
        })

        # 2. Historical Signals Sub-collection
        signals = [
            {"date": "2026-07-15", "entry": 2400.0, "target": 2550.0, "stop_loss": 2350.0, "outcome": "TARGET_HIT", "profit_pct": 6.25},
            {"date": "2026-07-28", "entry": 2500.0, "target": 2650.0, "stop_loss": 2450.0, "outcome": "STOP_LOSS", "profit_pct": -2.0},
            {"date": "2026-08-05", "entry": 2480.0, "target": 2620.0, "stop_loss": 2430.0, "outcome": "ACTIVE", "profit_pct": 0.5}
        ]

        # Adjust entry/target for TCS prices
        if symbol == "TCS":
            for s in signals:
                s["entry"] += 1200
                s["target"] += 1400
                s["stop_loss"] += 1150

        for i, sig in enumerate(signals):
            bt_ref.collection("signals").document(f"sig_{i}").set({
                **sig,
                "timestamp": datetime.datetime.utcnow() - datetime.timedelta(days=10-i)
            })

        print(f"   [+] Seeded Backtest: {symbol}")

if __name__ == "__main__":
    seed()
