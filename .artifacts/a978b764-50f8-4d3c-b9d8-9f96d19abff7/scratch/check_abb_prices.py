import sys
import os
from sqlalchemy import text
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')

from backend.core.postgres import engine

def check():
    with engine.connect() as conn:
        res = conn.execute(text("SELECT date, open, high, low, close FROM historical_prices WHERE symbol = 'ABB' ORDER BY date LIMIT 20"))
        print("--- ABB Prices ---")
        for r in res:
            print(r)

if __name__ == "__main__":
    check()
