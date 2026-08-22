
import sqlite3
import os

def main():
    db_path = "G:/TradeMindAI/backend/local_operational.db"
    if not os.path.exists(db_path):
        print(f"DB not found at {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("--- ALL SHADOW SIGNALS ---")
    cursor.execute("SELECT * FROM shadow_signals;")
    rows = cursor.fetchall()
    for row in rows:
        print(row)

    print("\n--- SHADOW EVENTS (LATEST 10) ---")
    cursor.execute("SELECT * FROM shadow_events ORDER BY timestamp DESC LIMIT 10;")
    rows = cursor.fetchall()
    for row in rows:
        print(row)

    conn.close()

if __name__ == "__main__":
    main()
