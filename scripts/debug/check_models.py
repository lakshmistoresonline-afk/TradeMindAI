import sys
import os
import sqlite3

# Set up paths
db_path = "backend/local_operational.db"

if __name__ == "__main__":
    if not os.path.exists(db_path):
        print(f"DB not found at {db_path}")
        sys.exit(1)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("=== CHAMPION MODELS ===")
    cursor.execute("SELECT symbol, horizon, is_champion, name FROM model_registry WHERE is_champion = 1 LIMIT 20;")
    rows = cursor.fetchall()
    for row in rows:
        print(row)

    cursor.execute("SELECT COUNT(*) FROM model_registry;")
    count = cursor.fetchone()[0]
    print(f"Total models in registry: {count}")

    conn.close()
