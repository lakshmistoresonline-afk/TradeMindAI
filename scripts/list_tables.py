import sqlite3
import os

db_path = 'backend/local_operational.db'
if not os.path.exists(db_path):
    print(f"Database not found at {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
for table in tables:
    print(table[0])
conn.close()
