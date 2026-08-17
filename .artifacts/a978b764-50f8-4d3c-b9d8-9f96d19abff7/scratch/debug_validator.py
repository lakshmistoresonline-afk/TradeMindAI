import os
import sys
from sqlalchemy import text
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')

from backend.core.postgres import engine
from scripts.universe.nifty200_canonical import NIFTY_200_CONSTITUENTS

def debug():
    with engine.connect() as conn:
        query = text("SELECT symbol, count(*) FROM historical_prices GROUP BY symbol")
        res = conn.execute(query).fetchall()
        db_symbols = {r[0] for r in res}
        print(f"Symbols in DB: {db_symbols}")

        expected_symbols = set(NIFTY_200_CONSTITUENTS)
        intersection = db_symbols.intersection(expected_symbols)
        print(f"Intersection count: {len(intersection)}")

        diff = db_symbols - expected_symbols
        print(f"Symbols in DB but not in NIFTY_200: {diff}")

        missing = expected_symbols - db_symbols
        print(f"Symbols in NIFTY_200 but not in DB: {len(missing)}")

if __name__ == "__main__":
    debug()
