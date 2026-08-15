import os
import sys
from sqlalchemy import text
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')

from backend.core.postgres import engine

def cleanup():
    with engine.connect() as conn:
        print("[*] STEP 1: Identifying Options signals with null Strike/Type...")
        res = conn.execute(text("DELETE FROM live_signals WHERE asset_class = 'OPTIONS' AND (strike IS NULL OR option_type IS NULL)"))
        print(f"   [+] Purged {res.rowcount} corrupt Options records.")

        print("[*] STEP 2: Identifying Futures signals with null Underlying...")
        res = conn.execute(text("DELETE FROM live_signals WHERE asset_class = 'FUTURES' AND underlying_symbol IS NULL"))
        print(f"   [+] Purged {res.rowcount} corrupt Futures records.")

        conn.commit()
        print("\n[SUCCESS] Aggressive Cleanup Complete.")

if __name__ == "__main__":
    cleanup()
