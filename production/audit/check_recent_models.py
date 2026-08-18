
import os
import sqlite3
import json

def check():
    db_path = os.path.join(os.getcwd(), "backend", "local_operational.db")
    if not os.path.exists(db_path):
        print("DB not found")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Check models trained on 2026-08-18 or 2026-08-17
    cursor.execute("SELECT symbol, name, last_trained, is_champion FROM model_registry WHERE last_trained >= '2026-08-17'")
    rows = cursor.fetchall()

    print(f"Models trained recently: {len(rows)}")
    for r in rows:
        print(f"Symbol: {r[0]}, Name: {r[1]}, Trained: {r[2]}, Champion: {r[3]}")

    # Count by symbol
    cursor.execute("SELECT count(DISTINCT symbol) FROM model_registry WHERE last_trained >= '2026-08-17' AND is_champion = 1")
    count = cursor.fetchone()[0]
    print(f"Unique champion symbols trained recently: {count}")

    conn.close()

if __name__ == "__main__":
    check()
