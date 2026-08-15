import os
import sys
from sqlalchemy import text
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

load_dotenv('backend/.env')

from backend.core.postgres import engine

def migrate():
    with engine.connect() as conn:
        print("[*] Extending schema for Futures & Options support...")
        # Add F&O columns to live_signals
        conn.execute(text("ALTER TABLE live_signals ADD COLUMN IF NOT EXISTS asset_class VARCHAR(20) DEFAULT 'EQUITY'"))
        conn.execute(text("ALTER TABLE live_signals ADD COLUMN IF NOT EXISTS underlying_symbol VARCHAR(20)"))
        conn.execute(text("ALTER TABLE live_signals ADD COLUMN IF NOT EXISTS strike FLOAT"))
        conn.execute(text("ALTER TABLE live_signals ADD COLUMN IF NOT EXISTS option_type VARCHAR(10)"))
        conn.execute(text("ALTER TABLE live_signals ADD COLUMN IF NOT EXISTS expiry TIMESTAMP"))
        conn.execute(text("ALTER TABLE live_signals ADD COLUMN IF NOT EXISTS lot_size INTEGER"))
        conn.commit()
        print("[+] F&O Schema Migration Complete.")

if __name__ == "__main__":
    migrate()
