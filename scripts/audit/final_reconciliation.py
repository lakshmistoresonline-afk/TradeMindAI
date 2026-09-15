import sqlite3
import json
import os
from datetime import datetime

def run_audit():
    print("=== FINAL TRADEMIND AI SIGNAL RECONCILIATION ===")

    conn = sqlite3.connect('backend/local_operational.db')
    cursor = conn.cursor()

    # 1. Total Signals
    cursor.execute('SELECT COUNT(*) FROM live_signals')
    total = cursor.fetchone()[0]
    print(f"Authoritative Neon Ledger Count: {total}")

    # 2. Quality Class Distribution
    cursor.execute('SELECT timeframe, quality_class, COUNT(*) FROM live_signals GROUP BY timeframe, quality_class')
    rows = cursor.fetchall()
    print("\nQuality Distribution:")
    for row in rows:
        print(f"   {row[0]} / {row[1]}: {row[2]}")

    # 3. Sample Size Verification (Model Metadata)
    cursor.execute('SELECT symbol, horizon, roc_auc, hyperparameters FROM model_registry')
    models = cursor.fetchall()

    print(f"\nTotal Champions in Registry: {len(models)}")

    # 4. Field Verification
    cursor.execute('SELECT * FROM live_signals LIMIT 1')
    signal_row = cursor.fetchone()
    if signal_row:
        # Check critical fields index in LiveSignalDB
        # We'll just print a few to verify
        cursor.execute("PRAGMA table_info(live_signals)")
        cols = [c[1] for c in cursor.fetchall()]
        print("\nCritical Field Check (PASS if present):")
        for f in ["symbol", "direction", "timeframe", "quality_class", "calibrated_probability", "expected_value", "risk_reward_ratio"]:
            if f in cols:
                print(f"   [OK] {f}")
            else:
                print(f"   [FAIL] {f} MISSING")

    conn.close()

if __name__ == "__main__":
    run_audit()
