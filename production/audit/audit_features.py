
import os
import sys
import duckdb
import pandas as pd
from datetime import datetime

def audit():
    feature_dir = "backend/data/features"
    if not os.path.exists(feature_dir):
        print(f"Feature directory not found at {feature_dir}")
        return

    files = [f for f in os.listdir(feature_dir) if f.endswith(".parquet")]
    print(f"Total feature files: {len(files)}")

    results = []
    for f in files:
        symbol = f.replace(".parquet", "")
        file_path = os.path.join(feature_dir, f)

        try:
            # Use duckdb to read parquet metadata or just count
            con = duckdb.connect()
            res = con.execute(f"SELECT count(*), max(date) FROM '{file_path}'").fetchone()
            count = res[0]
            last_date = res[1]
            con.close()

            results.append({
                "symbol": symbol,
                "count": count,
                "last_date": str(last_date)
            })
        except Exception as e:
            print(f"Error auditing {symbol}: {e}")

    df = pd.DataFrame(results)
    if not df.empty:
        print(df.sort_values("last_date", ascending=False).head(30))

        # Check staleness (if last_date < 2026-08-17)
        stale = df[df['last_date'] < '2026-08-17']
        print(f"Stale feature files (< 2026-08-17): {len(stale)}")

        df.to_json("production/audit/feature_audit.json", orient="records", indent=4)

if __name__ == "__main__":
    audit()
