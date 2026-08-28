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
        print("[*] Extending live_signals table for Step 2D Price Status...")
        try:
            conn.execute(text("ALTER TABLE live_signals ADD COLUMN IF NOT EXISTS price_status VARCHAR(50)"))
            print("   [+] Added price_status")
        except Exception as e:
            print(f"   [!] Error adding price_status: {e}")

        conn.commit()
    print("\n[SUCCESS] Migration Complete.")

if __name__ == "__main__":
    migrate()
