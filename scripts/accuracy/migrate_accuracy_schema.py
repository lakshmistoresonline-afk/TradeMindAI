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
        print("[*] Extending schema for Accuracy Parameters...")
        # Add delivery_rate, options_pcr, and sector_alpha if they don't exist
        conn.execute(text("ALTER TABLE stocks ADD COLUMN IF NOT EXISTS delivery_rate FLOAT DEFAULT 0.0"))
        conn.execute(text("ALTER TABLE stocks ADD COLUMN IF NOT EXISTS options_pcr FLOAT DEFAULT 1.0"))
        conn.execute(text("ALTER TABLE stocks ADD COLUMN IF NOT EXISTS sector_alpha FLOAT DEFAULT 0.0"))
        conn.commit()
        print("[+] Schema Migration Complete.")

if __name__ == "__main__":
    migrate()
