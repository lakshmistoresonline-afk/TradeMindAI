
import sqlite3
import pandas as pd
import numpy as np
import os
import json

def forensic_integrity_scan():
    db_path = "backend/local_operational.db"
    csv_path = "validation/shadow/shadow_observations.csv"

    issues = []

    # 1. Check for Synthetic Candles
    conn = sqlite3.connect(db_path)
    # Search for common mock patterns: Round numbers, sequential numbers, or 'source' labels
    cursor = conn.cursor()

    # Check PriceDB source field
    cursor.execute("SELECT source, count(*) FROM historical_prices GROUP BY source")
    sources = cursor.fetchall()
    for src, count in sources:
        if src and src.lower() in ["mock", "synthetic", "test", "dummy"]:
            issues.append(f"Synthetic source detected in PriceDB: {src} ({count} rows)")

    # Check for round numbers in Close prices (suspicious if too many)
    cursor.execute("SELECT close FROM historical_prices WHERE close IS NOT NULL")
    prices = [r[0] for r in cursor.fetchall()]
    if prices:
        round_count = sum(1 for p in prices if p is not None and p == float(int(p)))
        round_pct = round_count / len(prices)
        if round_pct > 0.3: # Suspiciously high round prices
            issues.append(f"High frequency of integer prices detected: {round_pct:.2%}")

    # 2. Check for Randomized Probabilities in log
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        probs = df['calibrated_probability'].dropna()
        if len(probs) >= 10:
            # Check for Uniform distribution (suspicious for real models)
            # Or exactly 0.5/1.0
            if (probs == 0.5).sum() > 2:
                issues.append("Suspicious 0.5 probabilities detected.")

    # 3. Check for Duplicate Timestamps for same symbol
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        dupes = df[df.duplicated(subset=['symbol', 'timestamp'])]
        if not dupes.empty:
            issues.append(f"Duplicate evaluations detected: {len(dupes)} instances")

    # 4. Result
    status = "SECURE" if not issues else "SHADOW_ISSUES_FOUND"

    result = {
        "status": status,
        "timestamp": pd.Timestamp.now().isoformat(),
        "issues": issues,
        "integrity_score": 1.0 if not issues else 0.0
    }

    os.makedirs("validation/results", exist_ok=True)
    with open("validation/results/shadow_data_integrity.json", "w") as f:
        json.dump(result, f, indent=4)

    print(f"Integrity Scan: {status}")
    if issues:
        for i in issues:
            print(f"  [!] {i}")

    conn.close()

if __name__ == "__main__":
    forensic_integrity_scan()
