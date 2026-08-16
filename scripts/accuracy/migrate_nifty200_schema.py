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
        print("[*] Extending stocks table for Nifty 200 F&O metadata...")
        # Add columns to stocks
        conn.execute(text("ALTER TABLE stocks ADD COLUMN IF NOT EXISTS is_fno BOOLEAN DEFAULT FALSE"))
        conn.execute(text("ALTER TABLE stocks ADD COLUMN IF NOT EXISTS lot_size INTEGER"))
        conn.execute(text("ALTER TABLE stocks ADD COLUMN IF NOT EXISTS index_weight FLOAT"))
        conn.commit()
        print("[+] Schema Migration Complete.")

if __name__ == "__main__":
    migrate()
