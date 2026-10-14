import sqlite3
import os

db_path = os.path.abspath('backend/trade_mind.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("--- SIGNAL COUNTS IN DATABASE ---")
tables_to_check = [
    'app_signal_cache',
    'app_trading_signals',
    'shadow_signals',
    'live_signals',
    'app_market_data'
]

for t in tables_to_check:
    try:
        cursor.execute(f"SELECT COUNT(*) FROM {t};")
        cnt = cursor.fetchone()[0]
        print(f"Table '{t}': {cnt:,} records")
    except Exception as e:
        print(f"Table '{t}': does not exist or error ({e})")

# Breakdown of app_signal_cache by signal_type
try:
    cursor.execute("SELECT signal_type, COUNT(*) FROM app_signal_cache GROUP BY signal_type;")
    print("\nBreakdown of app_signal_cache:")
    for row in cursor.fetchall():
        print(f"  - {row[0]}: {row[1]:,} signals")
except Exception as e:
    print("Cache breakdown error:", e)

conn.close()
