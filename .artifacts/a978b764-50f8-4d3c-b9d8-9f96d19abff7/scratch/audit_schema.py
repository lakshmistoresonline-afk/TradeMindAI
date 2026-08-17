import sqlite3
import os

def audit():
    db_path = 'backend/local_operational.db'
    if not os.path.exists(db_path):
        print(f"DB not found at {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("--- Historical Prices Schema ---")
    cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='historical_prices'")
    print(cursor.fetchone()[0])

    print("\n--- Stocks Schema ---")
    cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='stocks'")
    print(cursor.fetchone()[0])

    conn.close()

if __name__ == "__main__":
    audit()
