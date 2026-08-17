import os
import sys
from sqlalchemy import text
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')

from backend.core.postgres import engine

def debug():
    with engine.connect() as conn:
        res = conn.execute(text("SELECT symbol, index_membership FROM stocks WHERE symbol IN ('RELIANCE', 'TCS', 'ABB')"))
        print(f"Membership: {res.fetchall()}")

if __name__ == "__main__":
    debug()
