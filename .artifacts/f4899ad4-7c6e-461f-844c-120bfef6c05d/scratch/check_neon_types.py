
import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')

def check():
    pg_url = os.getenv("POSTGRES_URL")
    if not pg_url:
        print("POSTGRES_URL not found")
        return

    engine = create_engine(pg_url)
    with engine.connect() as conn:
        print("--- NEON COLUMN TYPES: historical_prices ---")
        query = text("""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = 'historical_prices'
        """)
        rows = conn.execute(query).fetchall()
        for r in rows:
            print(f"{r[0]}: {r[1]}")

if __name__ == "__main__":
    check()
