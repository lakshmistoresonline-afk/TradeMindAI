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
        print("[*] Extending stocks table with index_membership...")
        try:
            conn.execute(text("ALTER TABLE stocks ADD COLUMN IF NOT EXISTS index_membership VARCHAR(50)"))
            print("   [+] Added index_membership column.")
            conn.commit()
        except Exception as e:
            print(f"   [!] Error: {e}")

    print("\n[SUCCESS] Index Membership Migration Complete.")

if __name__ == "__main__":
    migrate()
