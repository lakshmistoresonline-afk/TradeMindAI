
import sqlite3
import os

def main():
    db_path = "G:/TradeMindAI/backend/local_operational.db"
    if not os.path.exists(db_path):
        print(f"DB not found at {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("--- SBIN SIGNALS ---")
    cursor.execute("SELECT * FROM shadow_signals WHERE symbol='SBIN';")
    rows = cursor.fetchall()
    for row in rows:
        print(row)

    print("\n--- TABLE SCHEMA ---")
    cursor.execute("PRAGMA table_info(shadow_signals);")
    for col in cursor.fetchall():
        print(col)

    conn.close()

if __name__ == "__main__":
    main()
