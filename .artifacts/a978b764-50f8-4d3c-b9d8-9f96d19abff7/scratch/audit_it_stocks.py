import sys
import os
from sqlalchemy import text
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')

from backend.core.postgres import engine

def audit():
    with engine.connect() as conn:
        res = conn.execute(text("SELECT symbol, sector, industry FROM stocks WHERE sector LIKE '%Technology%' OR sector LIKE '%Communication%'"))
        for row in res:
            print(row)

if __name__ == "__main__":
    audit()
