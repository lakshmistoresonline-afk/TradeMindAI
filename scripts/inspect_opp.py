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
        res = conn.execute(text("SELECT * FROM opportunities LIMIT 1")).mappings().first()
        print(f"Record: {res}")
        if res:
            print(f"Keys: {res.keys()}")
            for k, v in res.items():
                print(f"{k}: {v} ({type(v)})")

if __name__ == "__main__":
    check()
