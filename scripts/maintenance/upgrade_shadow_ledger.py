import os
import sys
from sqlalchemy import text
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')

from backend.core.postgres import engine

def run_upgrade():
    print("--- TRADEMIND AI: UPGRADING SHADOW LEDGER SCHEMA ---")

    columns_to_add = [
        ("strike", "FLOAT"),
        ("expiry", "TIMESTAMP"),
        ("option_type", "VARCHAR(10)")
    ]

    with engine.connect() as conn:
        for col_name, col_type in columns_to_add:
            try:
                conn.execute(text(f"ALTER TABLE shadow_signals ADD COLUMN {col_name} {col_type}"))
                print(f"  [+] Column added: {col_name}")
            except Exception as e:
                print(f"  [!] Skipping {col_name}: {e}")
        conn.commit()

    print("\n[SUCCESS] Schema upgrade complete.")

if __name__ == "__main__":
    run_upgrade()
