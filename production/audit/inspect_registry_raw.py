
import os
import sys
import json
import sqlite3
from datetime import datetime

def inspect():
    db_path = os.path.join(os.getcwd(), "backend", "local_operational.db")
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return

    conn = sqlite3.connect(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT name, symbol, version, is_champion FROM model_registry")
        rows = cursor.fetchall()

        print(f"Total entries in model_registry: {len(rows)}")

        champions = [r for r in rows if r[3] == 1]
        print(f"Champion models count: {len(champions)}")

        champion_symbols = sorted(list(set([r[1] for r in champions])))
        print(f"Unique symbols with champions: {len(champion_symbols)}")
        print(f"Symbols: {', '.join(champion_symbols)}")

        all_symbols = sorted(list(set([r[1] for r in rows])))

        audit_data = {
            "total_entries": len(rows),
            "champion_count": len(champions),
            "champion_symbols": champion_symbols,
            "all_symbols_in_registry": all_symbols
        }

        os.makedirs("production/audit", exist_ok=True)
        with open("production/audit/registry_inspection.json", "w") as f:
            json.dump(audit_data, f, indent=4)

    finally:
        conn.close()

if __name__ == "__main__":
    inspect()
