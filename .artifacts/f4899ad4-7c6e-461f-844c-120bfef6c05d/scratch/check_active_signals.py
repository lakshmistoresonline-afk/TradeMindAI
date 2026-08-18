
import sqlite3
import json

def check():
    conn = sqlite3.connect('backend/local_operational.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, symbol, status, calibrated_probability, expected_value, entry_price, target_price, stop_price, model_version, timestamp FROM shadow_signals WHERE status = 'ACTIVE'")
    rows = cursor.fetchall()
    print(f"Found {len(rows)} active signals.")
    for r in rows:
        print(r)
    conn.close()

if __name__ == "__main__":
    check()
