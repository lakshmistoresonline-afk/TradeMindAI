import sqlite3
import pandas as pd
import numpy as np

db_path = "backend/local_operational.db"

def verify_calibration():
    conn = sqlite3.connect(db_path)

    print("=== Signal Probability Bucket Audit (n=237) ===")
    query = "SELECT calibrated_probability FROM live_signals"
    probs = pd.read_sql_query(query, conn)['calibrated_probability']

    bins = [0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 1.0]
    buckets = pd.cut(probs, bins)
    counts = buckets.value_counts().sort_index()

    print("\nBucket Distribution:")
    for bucket, count in counts.items():
        print(f"{bucket}: {count} signals ({count/len(probs)*100:.1f}%)")

    # Check for extreme overconfidence
    extreme = len(probs[probs > 0.95])
    print(f"\nSignals with Probability > 95%: {extreme} ({extreme/len(probs)*100:.1f}%)")

    conn.close()

if __name__ == "__main__":
    verify_calibration()
