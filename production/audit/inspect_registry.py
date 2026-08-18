
import os
import sys
import json
import sqlite3
import pandas as pd
from datetime import datetime

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))

def inspect():
    db_path = os.path.join(os.getcwd(), "backend", "local_operational.db")
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return

    conn = sqlite3.connect(db_path)
    try:
        df = pd.read_sql_query("SELECT * FROM model_registry", conn)
        print(f"Total entries in model_registry: {len(df)}")
        print(f"Champion models count: {len(df[df['is_champion'] == 1])}")

        # Unique symbols with champion models
        champion_symbols = df[df['is_champion'] == 1]['symbol'].unique()
        print(f"Unique symbols with champions: {len(champion_symbols)}")
        print(f"Symbols: {', '.join(sorted(champion_symbols))}")

        # Check for non-champion models
        other_symbols = df[df['is_champion'] == 0]['symbol'].unique()
        print(f"Unique symbols without champions: {len(other_symbols)}")

        # Save to JSON for report
        audit_data = {
            "total_entries": int(len(df)),
            "champion_count": int(len(df[df['is_champion'] == 1])),
            "champion_symbols": sorted(champion_symbols.tolist()),
            "all_symbols_in_registry": sorted(df['symbol'].unique().tolist())
        }

        os.makedirs("production/audit", exist_ok=True)
        with open("production/audit/registry_inspection.json", "w") as f:
            json.dump(audit_data, f, indent=4)

    finally:
        conn.close()

if __name__ == "__main__":
    inspect()
