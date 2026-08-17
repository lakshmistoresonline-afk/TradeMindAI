import sys
import os
from sqlalchemy import text
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')

from backend.core.postgres import engine

def debug():
    with engine.connect() as conn:
        res = conn.execute(text("SELECT symbol, length(symbol) FROM historical_prices WHERE symbol LIKE 'HIND%' GROUP BY symbol"))
        print(f"Historical symbols starting with HIND: {res.fetchall()}")

        from scripts.universe.nifty200_canonical import NIFTY_200_CONSTITUENTS
        hind_in_canonical = [s for s in NIFTY_200_CONSTITUENTS if s.startswith('HIND')]
        print(f"Canonical symbols starting with HIND: {[(s, len(s)) for s in hind_in_canonical]}")

if __name__ == "__main__":
    debug()
