
import sqlite3
import os

def check():
    db_path = "backend/local_operational.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    symbols = ["GUJGASLTD", "TATAMOTORS", "PEL", "LTIM"]
    for s in symbols:
        cursor.execute("SELECT count(*) FROM historical_prices WHERE symbol = ?", (s,))
        print(f"{s}: {cursor.fetchone()[0]} rows")

    conn.close()

if __name__ == "__main__":
    check()
