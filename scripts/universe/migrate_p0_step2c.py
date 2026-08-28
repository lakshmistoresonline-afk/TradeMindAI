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
        print("[*] Extending live_signals table for Step 2C Price Resolution...")
        columns = [
            ("instrument_id", "VARCHAR(255)"),
            ("instrument_type", "VARCHAR(50)"),
            ("current_price", "DOUBLE PRECISION"),
            ("underlying_price", "DOUBLE PRECISION"),
            ("current_price_timestamp", "TIMESTAMP"),
            ("price_source", "VARCHAR(100)")
        ]

        for col_name, col_type in columns:
            try:
                conn.execute(text(f"ALTER TABLE live_signals ADD COLUMN IF NOT EXISTS {col_name} {col_type}"))
                print(f"   [+] Added {col_name}")
            except Exception as e:
                print(f"   [!] Error adding {col_name}: {e}")

        conn.commit()
    print("\n[SUCCESS] Live Signals Step 2C Migration Complete.")

if __name__ == "__main__":
    migrate()
