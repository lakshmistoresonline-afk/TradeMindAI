
import sqlite3
import json
import os
from datetime import datetime, timedelta

# Import universe
import sys
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
from scripts.universe.nifty200_canonical import NIFTY_200_CONSTITUENTS

def generate():
    db_path = "backend/local_operational.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    now = datetime.utcnow()

    results = []

    for symbol in NIFTY_200_CONSTITUENTS:
        # 1. Historical Data
        cursor.execute("SELECT count(*) FROM historical_prices WHERE symbol = ?", (symbol,))
        hist_count = cursor.fetchone()[0]
        hist_ok = hist_count > 500 # Threshold for "sufficient"

        # 2. Fresh Data
        cursor.execute("SELECT max(date) FROM historical_prices WHERE symbol = ?", (symbol,))
        last_date_str = cursor.fetchone()[0]
        if last_date_str:
            last_date = datetime.fromisoformat(last_date_str.split(".")[0])
            fresh_ok = (now - last_date).total_seconds() < 86400
        else:
            fresh_ok = False

        # 3. Model Compatibility
        cursor.execute("SELECT name, hyperparameters FROM model_registry WHERE symbol = ? AND is_champion = 1", (symbol,))
        model_row = cursor.fetchone()
        if model_row:
            name, hyper_json = model_row
            hypers = json.loads(hyper_json) if hyper_json else {}
            feature_count = len(hypers.get("feature_names", []))
            model_compatible = (feature_count == 11)
        else:
            model_compatible = False

        # 4. Liquidity (using avg_volume from stocks table if available)
        cursor.execute("SELECT avg_volume FROM stocks WHERE symbol = ?", (symbol,))
        vol_row = cursor.fetchone()
        avg_vol = vol_row[0] if vol_row and vol_row[0] else 0
        liq_ok = (avg_vol >= 10_000_000)

        eligible = hist_ok and fresh_ok and model_compatible and liq_ok

        results.append({
            "Symbol": symbol,
            "Historical": "YES" if hist_ok else f"NO ({hist_count})",
            "Fresh": "YES" if fresh_ok else "STALE",
            "Model": "v2.2" if model_compatible else "MISSING",
            "Liquidity": "PASS" if liq_ok else f"FAIL ({int(avg_vol/1e6)}M)",
            "Eligible": "YES" if eligible else "NO"
        })

    # Save to JSON
    os.makedirs("production/audit", exist_ok=True)
    with open("production/audit/universe_eligibility.json", "w") as f:
        json.dump(results, f, indent=4)

    print(f"Universe table generated for {len(results)} symbols.")
    conn.close()

if __name__ == "__main__":
    generate()
