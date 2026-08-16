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
        print("[*] Starting ABSOLUTE Data Purge...")

        # 1. Purge ALL signals to reset accuracy metrics and remove P0-incompatible nodes
        print("[*] Purging ALL records from live_signals...")
        res = conn.execute(text("DELETE FROM live_signals"))
        print(f"   [+] Purged {res.rowcount} signal records.")

        # 2. Purge ML Artifacts
        print("[*] Purging predictions and opportunities...")
        conn.execute(text("DELETE FROM predictions"))
        conn.execute(text("DELETE FROM opportunities"))

        # 3. Clean up technical master data
        print("[*] Cleaning up stocks table...")
        conn.execute(text("DELETE FROM stocks WHERE name = 'Data Corrupted' OR name = 'Unknown'"))

        conn.commit()
        print("\n[SUCCESS] Production database is now 100% clean and P0-ready.")

if __name__ == "__main__":
    cleanup()
