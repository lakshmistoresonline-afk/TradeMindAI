
import os
import sqlite3

def check():
    db_path = os.path.join(os.getcwd(), "backend", "local_operational.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT count(*) FROM stocks")
    count = cursor.fetchone()[0]
    print(f"Total entries in stocks table: {count}")

    cursor.execute("SELECT symbol, last_price, avg_volume FROM stocks LIMIT 10")
    rows = cursor.fetchall()
    for r in rows:
        print(f"Symbol: {r[0]}, Price: {r[1]}, Avg Vol: {r[2]}")

    conn.close()

if __name__ == "__main__":
    check()
