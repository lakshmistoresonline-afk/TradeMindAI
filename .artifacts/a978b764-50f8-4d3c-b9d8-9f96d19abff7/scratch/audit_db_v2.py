import sys
import os
from sqlalchemy import text
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')

from backend.core.postgres import engine

def audit():
    with engine.connect() as conn:
        print("--- Stock Master Check ---")
        symbols = ['LTIM', 'PEL', 'ZOMATO']
        res = conn.execute(text(f"SELECT symbol FROM stocks WHERE symbol IN {tuple(symbols)}"))
        print(f"Master records found: {res.fetchall()}")

        print("\n--- Historical Prices Check ---")
        res = conn.execute(text(f"SELECT symbol, count(*) FROM historical_prices WHERE symbol IN {tuple(symbols)} GROUP BY symbol"))
        print(f"Historical counts: {res.fetchall()}")

        print("\n--- Partial Stocks Check (< 500 rows) ---")
        res = conn.execute(text("SELECT symbol, count(*) as c, min(date), max(date) FROM historical_prices GROUP BY symbol HAVING count(*) < 500"))
        for row in res:
            print(row)

if __name__ == "__main__":
    audit()
