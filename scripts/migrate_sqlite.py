import sqlite3
import os

db_path = 'D:/TradeMindAI/local_operational.db'

if not os.path.exists(db_path):
    print("[*] Local DB not found. No migration needed.")
    exit(0)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get existing columns
cursor.execute("PRAGMA table_info(stocks)")
existing_cols = [row[1] for row in cursor.fetchall()]

# Columns to add for Vision 2.2
required_cols = [
    ("ai_investment_score", "FLOAT"),
    ("ai_investment_grade", "TEXT"),
    ("ai_status", "TEXT DEFAULT 'PENDING'"),
    ("ai_last_error", "TEXT"),
    ("analysis", "TEXT"),
    ("structured_consensus", "TEXT"),
    ("options_data", "TEXT"),
    ("financial_history", "TEXT"),
    ("health_metrics", "TEXT"),
    ("confidence_metrics", "TEXT")
]

added = 0
for col_name, col_type in required_cols:
    if col_name not in existing_cols:
        print(f"[*] Adding column {col_name} to stocks table...")
        try:
            cursor.execute(f"ALTER TABLE stocks ADD COLUMN {col_name} {col_type}")
            added += 1
        except Exception as e:
            print(f"   [!] Failed to add {col_name}: {e}")

conn.commit()
conn.close()

print(f"[+] Migration complete. Added {added} columns.")
