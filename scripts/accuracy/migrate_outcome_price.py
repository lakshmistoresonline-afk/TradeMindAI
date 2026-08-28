import os
import sys
from sqlalchemy import text
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')

from backend.core.postgres import engine

def migrate():
    with engine.connect() as conn:
        print("[*] Adding outcome_price to live_signals...")
        conn.execute(text("ALTER TABLE live_signals ADD COLUMN IF NOT EXISTS outcome_price FLOAT"))
        conn.commit()
        print("[+] Migration Complete.")

if __name__ == "__main__":
    migrate()
