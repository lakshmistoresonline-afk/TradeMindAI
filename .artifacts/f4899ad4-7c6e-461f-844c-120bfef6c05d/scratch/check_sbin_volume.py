
import sqlite3
import pandas as pd

def check():
    db_path = "backend/local_operational.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT avg(volume) FROM historical_prices WHERE symbol = 'SBIN'")
    print(f"SBIN Avg Volume: {cursor.fetchone()[0]}")

    cursor.execute("SELECT count(*) FROM historical_prices WHERE symbol = 'SBIN' AND volume > 10000000")
    print(f"SBIN bars with volume > 10M: {cursor.fetchone()[0]}")

    conn.close()

if __name__ == "__main__":
    check()
