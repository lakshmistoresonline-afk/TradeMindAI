
import os
import sys
import sqlite3

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))

from scripts.universe.nifty200_canonical import NIFTY_200_CONSTITUENTS

def compare():
    db_path = os.path.join(os.getcwd(), "backend", "local_operational.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT DISTINCT symbol FROM model_registry WHERE is_champion = 1")
    db_symbols = [r[0] for r in cursor.fetchall()]
    db_pure = set([s for s in db_symbols if "_" not in s])

    universe = set(NIFTY_200_CONSTITUENTS)

    in_db_in_univ = db_pure.intersection(universe)
    in_db_not_univ = db_pure.difference(universe)
    in_univ_not_db = universe.difference(db_pure)

    print(f"Total in Universe: {len(universe)}")
    print(f"Total in DB (pure): {len(db_pure)}")
    print(f"Champions in Universe: {len(in_db_in_univ)}")
    print(f"Champions NOT in Universe: {len(in_db_not_univ)}")
    if in_db_not_univ: print(f"  Extra: {', '.join(sorted(in_db_not_univ))}")
    print(f"Missing from DB: {len(in_univ_not_db)}")

    conn.close()

if __name__ == "__main__":
    compare()
