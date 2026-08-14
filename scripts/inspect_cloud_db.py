import os
import sys
import json
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load backend environment variables
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend", ".env")
load_dotenv(env_path)

db_url = os.getenv("POSTGRES_URL")
print(f"[*] Connecting to: {db_url[:20]}...")

def inspect():
    engine = create_engine(db_url)
    symbols = ['CONCOR', 'BIOCON', 'BALKRISIND']
    with engine.connect() as conn:
        query = text("SELECT symbol, last_price, structured_consensus, ai_status FROM stocks WHERE symbol IN :symbols")
        result = conn.execute(query, {"symbols": tuple(symbols)})
        for row in result:
            print(f"--- {row.symbol} ---")
            print(f"Price: {row.last_price}")
            print(f"Consensus: {row.structured_consensus}")
            print(f"Status: {row.ai_status}")

if __name__ == "__main__":
    inspect()
