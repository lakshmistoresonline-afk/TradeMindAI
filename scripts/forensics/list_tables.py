import sqlite3

db_path = "backend/local_operational.db"

def list_tables():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    for table in tables:
        print(table[0])
    conn.close()

if __name__ == "__main__":
    list_tables()
