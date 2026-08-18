
import os
import sys
import pandas as pd
import numpy as np
from sqlalchemy import text
from dotenv import load_dotenv
import json

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')

from backend.core.container import container
from backend.core.postgres import engine

def monitor_drift():
    print("--- PRODUCTION DRIFT MONITORING ---")

    # 1. Load Baseline
    baseline_path = "validation/results/production_certification.json"
    if not os.path.exists(baseline_path):
        print("[!] Certification baseline missing.")
        return

    with open(baseline_path, 'r') as f:
        baseline = json.load(f)

    # 2. Fetch Shadow Performance
    with engine.connect() as conn:
        query = text("SELECT status, net_return, raw_probability FROM shadow_signals WHERE status != 'ACTIVE'")
        df = pd.read_sql(query, conn)

        if df.empty:
            print("[INFO] Insufficient shadow data for drift analysis.")
            return

        resolved = df[df['status'].isin(['TARGET_HIT', 'STOP_LOSS'])]
        if resolved.empty:
             print("[INFO] No resolved shadow trades yet.")
             return

        live_wr = (resolved['status'] == 'TARGET_HIT').mean() * 100
        live_ev = resolved['net_return'].mean()

        print(f"\n[Performance Comparison]")
        print(f"Baseline WR: {baseline['weighted_win_rate']:.2f}% | Live WR: {live_wr:.2f}%")
        print(f"Baseline EV: {baseline['net_ev_per_trade']:.4f}% | Live EV: {live_ev:.4f}%")

        # 3. Detect Drift
        wr_drift = live_wr - baseline['weighted_win_rate']
        ev_drift = live_ev - baseline['net_ev_per_trade']

        status = "STABLE"
        if abs(wr_drift) > 10 or ev_drift < -0.5:
            status = "DRIFT_DETECTED"
            print(f"[WARNING] Significant performance drift detected! WR Delta: {wr_drift:.2f}%")

        # Save Drift Report
        report = {
            "timestamp": pd.Timestamp.now().isoformat(),
            "status": status,
            "metrics": {
                "wr_drift": round(float(wr_drift), 2),
                "ev_drift": round(float(ev_drift), 4),
                "sample_size": int(len(resolved))
            }
        }

        os.makedirs("production/monitoring", exist_ok=True)
        with open("production/monitoring/DRIFT_REPORT.json", "w") as f:
            json.dump(report, f, indent=4)

        print(f"\nDrift Status: {status}")

if __name__ == "__main__":
    monitor_drift()
