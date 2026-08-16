import sqlite3
import os

def check():
    db_path = 'backend/local_operational.db'
    if not os.path.exists(db_path):
        print(f"❌ Database not found at {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("\n--- OPERATIONAL SQL AUDIT ---")

    tables = ["stocks", "historical_prices", "market_regimes", "predictions", "intel_reports"]
    for table in tables:
        try:
            cursor.execute(f"SELECT count(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"[{table:.<20}] {count} records")
        except Exception as e:
            print(f"[{table:.<20}] ❌ ERROR: {e}")

    conn.close()

if __name__ == "__main__":
    check()
