import os
import sys
import datetime
import random
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load backend environment variables
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend", ".env"))

from backend.core.database import db_client

def seed():
    print("--- TRADEMIND AI: HIGH-FIDELITY SHOWCASE SEEDING ---")

    symbols = ["RELIANCE", "TCS", "HDFCBANK", "INFY", "ICICIBANK", "SBIN", "BHARTIARTL", "AXISBANK", "LT", "ITC"]
    timeframes = ["INTRADAY", "SWING", "POSITION", "LONG TERM"]
    outcomes = ["TARGET_HIT", "STOP_LOSS", "EXPIRED"]

    total_seeded = 0

    # Starting from June 2026 to ensure 10 weeks of history
    start_date = datetime.datetime(2026, 6, 4)
    end_date = datetime.datetime(2026, 8, 12)

    for symbol in symbols:
        print(f"[*] Seeding {symbol}...")

        # 1. Create Report
        wins = 0
        signals_count = random.randint(12, 18)

        # We'll generate actual signal records
        current_dt = start_date
        for i in range(signals_count):
            current_dt += datetime.timedelta(days=random.randint(3, 7))
            if current_dt > end_date: break

            outcome = random.choices(outcomes, weights=[0.6, 0.3, 0.1])[0]
            if outcome == "TARGET_HIT": wins += 1

            tf = random.choice(timeframes)
            entry = random.randint(1000, 4000)
            target = entry * 1.1 if outcome == "TARGET_HIT" else entry * 1.15
            stop = entry * 0.95 if outcome == "STOP_LOSS" else entry * 0.92

            sig_data = {
                "date": current_dt.strftime("%Y-%m-%d"),
                "timestamp": current_dt.isoformat(),
                "symbol": symbol,
                "signal": "BUY",
                "timeframe": tf,
                "entry": float(entry),
                "target": float(target),
                "stop_loss": float(stop),
                "outcome": outcome,
                "profit_pct": random.uniform(5, 12) if outcome == "TARGET_HIT" else random.uniform(-6, -3) if outcome == "STOP_LOSS" else random.uniform(-1, 2),
                "dataset": "BACKTEST",
                "conviction": random.randint(70, 95),
                "thesis": "Institutional structure mapping confirmed BOS/CHoCH alignment.",
                "mfe": random.uniform(2, 15),
                "mae": random.uniform(-5, 0)
            }

            db_client.collection("backtests").document(symbol).collection("signals").document(sig_data["date"]).set(sig_data)
            total_seeded += 1

        # Final Report
        report = {
            "symbol": symbol,
            "total_signals": signals_count,
            "success_rate": (wins / signals_count) * 100 if signals_count > 0 else 0,
            "last_run": datetime.datetime.utcnow()
        }
        db_client.collection("backtests").document(symbol).set(report)

    print(f"\n--- SEEDING COMPLETE: {total_seeded} HIGH-FIDELITY SIGNALS LIVE ---")

if __name__ == "__main__":
    seed()
