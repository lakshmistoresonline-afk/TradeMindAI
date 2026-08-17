import sys
import os
from sqlalchemy import text
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')

from backend.core.postgres import engine

def update():
    with engine.connect() as conn:
        print("[*] Updating last_price from historical_prices...")
        query = text("""
            UPDATE stocks
            SET last_price = (
                SELECT close FROM historical_prices
                WHERE historical_prices.symbol = stocks.symbol
                ORDER BY date DESC LIMIT 1
            )
            WHERE last_price IS NULL OR last_price = 0
        """)
        res = conn.execute(query)
        conn.commit()
        print(f"[SUCCESS] Updated {res.rowcount} stocks.")

if __name__ == "__main__":
    update()
