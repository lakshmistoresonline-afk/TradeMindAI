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
        print("[*] Extending instruments table for P0 F&O master data...")
        columns = [
            ("underlying_symbol", "VARCHAR(50)"),
            ("lot_size", "INTEGER"),
            ("tick_size", "DOUBLE PRECISION")
        ]

        for col_name, col_type in columns:
            try:
                conn.execute(text(f"ALTER TABLE instruments ADD COLUMN IF NOT EXISTS {col_name} {col_type}"))
                print(f"   [+] Added {col_name}")
            except Exception as e:
                print(f"   [!] Error adding {col_name}: {e}")

        conn.commit()
    print("\n[SUCCESS] Instruments Schema Migration Complete.")

if __name__ == "__main__":
    migrate()
