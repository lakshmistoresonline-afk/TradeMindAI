import os
import sys
from sqlalchemy import text
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')

from backend.core.postgres import engine

def run():
    print("--- TRADEMIND AI: RENAMING stop_loss_price -> stop_price ---")

    with engine.connect() as conn:
        try:
            # Check if column exists in live_signals
            res = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'live_signals' AND column_name = 'stop_loss_price'")).fetchone()
            if res:
                conn.execute(text("ALTER TABLE live_signals RENAME COLUMN stop_loss_price TO stop_price"))
                print("[+] Renamed column in live_signals.")
            else:
                print("[!] stop_loss_price not found in live_signals (already renamed?).")

            conn.commit()
            print("[SUCCESS] Column rename complete.")
        except Exception as e:
            print(f"[FAILED] Error: {e}")
            conn.rollback()

if __name__ == "__main__":
    run()
