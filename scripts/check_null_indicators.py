import os
import sys
from sqlalchemy import text
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load backend environment variables
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend", ".env"))

from backend.core.postgres import engine

def check():
    with engine.connect() as conn:
        res = conn.execute(text("SELECT symbol FROM opportunities WHERE indicators IS NULL")).all()
        print(f"Opportunities with NULL indicators: {len(res)}")
        for r in res:
            print(f"   - {r[0]}")

if __name__ == "__main__":
    check()
