
import os
import sqlite3

def check():
    db_path = os.path.join(os.getcwd(), "backend", "local_operational.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT is_champion, count(*) FROM model_registry GROUP BY is_champion")
    rows = cursor.fetchall()
    for r in rows:
        print(f"Value: {r[0]} (Type: {type(r[0])}), Count: {r[1]}")

    conn.close()

if __name__ == "__main__":
    check()
