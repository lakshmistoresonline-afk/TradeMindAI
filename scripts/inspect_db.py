import sqlite3
import os

db_path = os.path.abspath('backend/trade_mind.db')
print('Database Path:', db_path)
if not os.path.exists(db_path):
    print('Database file not found!')
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print('Tables:', [t[0] for t in tables])

for t in tables:
    t_name = t[0]
    try:
        cursor.execute(f"SELECT COUNT(*) FROM {t_name};")
        cnt = cursor.fetchone()[0]
        print(f"  - {t_name}: {cnt} rows")
    except Exception as e:
        print(f"  - {t_name}: error {e}")

# Check sample signal cache records
try:
    cursor.execute("SELECT symbol, signal_type, confidence FROM app_signal_cache LIMIT 5;")
    print('Sample app_signal_cache:', cursor.fetchall())
except Exception as e:
    print('app_signal_cache query error:', e)

conn.close()
