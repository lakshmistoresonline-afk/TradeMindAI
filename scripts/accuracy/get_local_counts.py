import sqlite3
import os

db_path = 'backend/local_operational.db'
conn = sqlite3.connect(db_path)
tables = [
    'stocks', 'historical_prices', 'live_signals', 'shadow_signals',
    'market_regimes', 'instruments', 'shadow_scan_diagnostics'
]

print("Table | Count")
print("--- | ---")
for table in tables:
    count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    print(f"{table} | {count}")

# Special check for LTIM and GUJGASLTD in historical_prices
for s in ['LTIM', 'GUJGASLTD']:
    c = conn.execute("SELECT COUNT(*) FROM historical_prices WHERE symbol=?", (s,)).fetchone()[0]
    print(f"DEBUG: historical_prices({s}) | {c}")

conn.close()
