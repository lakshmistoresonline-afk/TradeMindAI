
import os
import sqlite3

def inspect():
    db_path = os.path.join(os.getcwd(), "local_operational.db")
    if not os.path.exists(db_path):
        print("Root DB not found")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT count(*) FROM model_registry WHERE is_champion = 1")
        count = cursor.fetchone()[0]
        print(f"Champions in Root DB: {count}")

        cursor.execute("SELECT DISTINCT symbol FROM model_registry WHERE is_champion = 1")
        symbols = [r[0] for r in cursor.fetchall()]
        pure_symbols = [s for s in symbols if "_" not in s]
        print(f"Pure symbols in Root DB: {len(pure_symbols)}")
        print(f"Symbols: {', '.join(sorted(pure_symbols))}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    inspect()
