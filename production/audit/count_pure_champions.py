
import os
import sqlite3

def check():
    db_path = os.path.join(os.getcwd(), "backend", "local_operational.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT DISTINCT symbol FROM model_registry WHERE is_champion = 1")
    symbols = [r[0] for r in cursor.fetchall()]

    pure_symbols = [s for s in symbols if "_" not in s]

    print(f"Total symbols with champions: {len(symbols)}")
    print(f"Pure symbols with champions: {len(pure_symbols)}")
    print(f"Pure Symbols: {', '.join(sorted(pure_symbols))}")

    conn.close()

if __name__ == "__main__":
    check()
