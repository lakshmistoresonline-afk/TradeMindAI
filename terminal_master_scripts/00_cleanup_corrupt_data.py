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
        print("[*] Starting Data Forensic Cleanup...")

        # 1. Purge all generated signals to ensure a 100% clean baseline
        # This covers all prefixes used in manual population scripts.
        print("[*] Purging all manual/generated signals across segments...")
        res = conn.execute(text("DELETE FROM live_signals WHERE id LIKE 'live_%' OR id LIKE 'master_%' OR id LIKE 'audit_%' OR id LIKE 'hist_%' OR id LIKE 'fno_%' OR id LIKE 'sig_%' OR id LIKE 'prec_%'"))
        print(f"[+] Purged {res.rowcount} generated signal records.")

        # 2. Fix technical master data
        print("[*] Cleaning up orphaned stock records...")
        res = conn.execute(text("DELETE FROM stocks WHERE name = 'Data Corrupted' OR name = 'Unknown'"))
        print(f"[+] Deleted {res.rowcount} invalid stock master records.")

        conn.commit()
        print("\n[SUCCESS] Database Cleanup Complete. System nodes are now 100% clean.")

if __name__ == "__main__":
    cleanup()
