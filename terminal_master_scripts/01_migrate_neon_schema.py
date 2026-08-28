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
        print("[*] STEP 1: Extending live_signals table...")
        # Signal metadata columns
        conn.execute(text("ALTER TABLE live_signals ADD COLUMN IF NOT EXISTS asset_class VARCHAR(20) DEFAULT 'EQUITY'"))
        conn.execute(text("ALTER TABLE live_signals ADD COLUMN IF NOT EXISTS underlying_symbol VARCHAR(20)"))
        conn.execute(text("ALTER TABLE live_signals ADD COLUMN IF NOT EXISTS strike FLOAT"))
        conn.execute(text("ALTER TABLE live_signals ADD COLUMN IF NOT EXISTS option_type VARCHAR(10)"))
        conn.execute(text("ALTER TABLE live_signals ADD COLUMN IF NOT EXISTS expiry TIMESTAMP"))
        conn.execute(text("ALTER TABLE live_signals ADD COLUMN IF NOT EXISTS lot_size INTEGER"))

        # Outcome Tracking
        conn.execute(text("ALTER TABLE live_signals ADD COLUMN IF NOT EXISTS outcome_price FLOAT"))
        print("[+] live_signals schema updated.")

        print("[*] STEP 2: Extending stocks table...")
        # Stock master metadata columns
        conn.execute(text("ALTER TABLE stocks ADD COLUMN IF NOT EXISTS is_fno BOOLEAN DEFAULT FALSE"))
        conn.execute(text("ALTER TABLE stocks ADD COLUMN IF NOT EXISTS lot_size INTEGER"))
        conn.execute(text("ALTER TABLE stocks ADD COLUMN IF NOT EXISTS index_weight FLOAT"))
        print("[+] stocks schema updated.")

        conn.commit()
        print("\n[SUCCESS] Master Neon Schema Migration Complete.")

if __name__ == "__main__":
    migrate()
