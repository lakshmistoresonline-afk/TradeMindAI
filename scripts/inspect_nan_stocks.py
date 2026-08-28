import os
import sys
import json
from sqlalchemy import text
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load backend environment variables
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend", ".env"))

from backend.core.postgres import SessionLocal, StockDB

def inspect_stocks():
    session = SessionLocal()
    symbols = ['CONCOR', 'BIOCON', 'BALKRISIND']
    try:
        stocks = session.query(StockDB).filter(StockDB.symbol.in_(symbols)).all()
        for s in stocks:
            print(f"--- Symbol: {s.symbol} ---")
            print(f"Last Price: {s.last_price}")
            print(f"Structured Consensus: {s.structured_consensus}")
            print(f"AI Status: {s.ai_status}")
            print("-" * 20)
    finally:
        session.close()

if __name__ == "__main__":
    inspect_stocks()
