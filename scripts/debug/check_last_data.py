import sqlite3
from datetime import datetime

conn = sqlite3.connect('backend/local_operational.db')
cursor = conn.cursor()
cursor.execute('SELECT symbol, MAX(timestamp) FROM features GROUP BY symbol LIMIT 10')
rows = cursor.fetchall()
print(f"Current System Time: {datetime.utcnow()}")
for row in rows:
    print(f"{row[0]}: {row[1]}")
conn.close()
