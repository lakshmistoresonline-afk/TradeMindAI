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
        res = conn.execute(text("SELECT count(*) FROM historical_prices WHERE symbol LIKE '%.NS'"))
        print(f"Rows with .NS: {res.scalar()}")

        res = conn.execute(text("SELECT DISTINCT symbol FROM historical_prices WHERE symbol LIKE '%.NS'"))
        print(f"Symbols with .NS: {res.fetchall()}")

if __name__ == "__main__":
    debug()
