
import os
import sys
import json
import sqlite3
from datetime import datetime

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))

def verify():
    db_path = "backend/local_operational.db"
    BASELINE_START = "2026-08-18"

    conn = sqlite3.connect(db_path)

    # 1. Trigger Count
    count_trigger = conn.execute(f"SELECT count(*) FROM shadow_events WHERE decision = 'TRADE_SIGNAL' AND timestamp >= '{BASELINE_START}'").fetchone()[0]

    # 2. Total Evaluations
    count_eval = conn.execute(f"SELECT count(*) FROM shadow_events WHERE event_type = 'EVALUATION' AND timestamp >= '{BASELINE_START}'").fetchone()[0]

    # 3. Prob Mean
    rows = conn.execute(f"SELECT payload_json FROM shadow_events WHERE event_type = 'EVALUATION' AND timestamp >= '{BASELINE_START}'").fetchall()
    probs = []
    for r in rows:
        if r[0]:
            p = json.loads(r[0]).get('prob')
            if p is not None:
                probs.append(p)

    prob_mean = sum(probs) / len(probs) if probs else 0

    print(f"Authoritative Metrics (Baseline: {BASELINE_START}):")
    print(f"  Evaluation Events: {count_eval}")
    print(f"  Strategy Trigger Events: {count_trigger}")
    print(f"  Probability Mean: {prob_mean:.4f}")

    # 4. Check for regression
    sbin_resolved = conn.execute("SELECT status, net_return FROM shadow_signals WHERE id='sig_SBIN_202608180715'").fetchone()
    print(f"  SBIN Resolved Signal: {sbin_resolved}")

    sbin_active = conn.execute("SELECT status FROM shadow_signals WHERE id='sig_SBIN_202608181011'").fetchone()
    print(f"  SBIN Active Signal: {sbin_active}")

    conn.close()

if __name__ == "__main__":
    verify()
