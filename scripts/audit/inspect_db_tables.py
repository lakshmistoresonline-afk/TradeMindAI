import sqlite3
import os

db_path = r"D:\TradeMindAI\backend\local_operational.db"
if not os.path.exists(db_path):
    print(f"Database file not found at {db_path}")
else:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
    tables = [row[0] for row in cursor.fetchall()]
    print(f"=== SQLite Database File ({db_path}) ===")
    print(f"Total Tables On Disk: {len(tables)}\n")
    for table in tables:
        if table.startswith("sqlite_"):
            continue
        try:
            cursor.execute(f"SELECT count(*) FROM [{table}]")
            count = cursor.fetchone()[0]

            # Get columns
            cursor.execute(f"PRAGMA table_info([{table}])")
            columns = cursor.fetchall()
            col_names = [c[1] for c in columns]

            print(f"Table: [{table}] ({count} rows)")
            print(f"  Columns ({len(col_names)}): {', '.join(col_names[:10])}{'...' if len(col_names) > 10 else ''}\n")
        except Exception as e:
            print(f"Table: [{table}] Error: {e}\n")
    conn.close()
