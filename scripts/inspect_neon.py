import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

load_dotenv('backend/.env')

def inspect():
    url = os.getenv("POSTGRES_URL")
    engine = create_engine(url)

    with engine.connect() as conn:
        print("\n--- STOCKS CHANGE_PCT CHECK ---")
        res = conn.execute(text("SELECT symbol, change_pct FROM stocks LIMIT 15"))
        for row in res:
            print(row)

        print("\n--- MARKET INTEL CHECK ---")
        res = conn.execute(text("SELECT type, date, summary FROM intel_reports ORDER BY date DESC LIMIT 1"))
        for row in res:
            print(row)

if __name__ == "__main__":
    inspect()
