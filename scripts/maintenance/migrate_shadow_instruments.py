import os
import sys
from sqlalchemy import text
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')

from backend.core.postgres import engine

def add_column_if_not_exists(conn, table, column, data_type):
    """Idempotently adds a column to a table."""
    try:
        # Check if column exists
        if "postgresql" in str(engine.url):
            query = text(f"SELECT 1 FROM information_schema.columns WHERE table_name='{table}' AND column_name='{column}'")
            exists = conn.execute(query).fetchone()
        else:
            query = text(f"PRAGMA table_info({table})")
            res = conn.execute(query).fetchall()
            exists = any(row[1] == column for row in res)

        if not exists:
            print(f"   [+] Adding {column} to {table}...")
            conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {data_type}"))
            conn.commit()
        else:
            print(f"   [ ] Column {column} already exists in {table}.")
    except Exception as e:
        print(f"   [!] Error adding {column} to {table}: {e}")

def run_migration():
    print("--- TRADEMIND AI: SHADOW INSTRUMENT MIGRATION ---")

    with engine.connect() as conn:
        cols_shadow = [
            ("asset_class", "VARCHAR(20) DEFAULT 'EQUITY'"),
            ("instrument_id", "VARCHAR"),
            ("instrument_type", "VARCHAR")
        ]

        print("[*] Migrating shadow_signals...")
        for col, dtype in cols_shadow:
            add_column_if_not_exists(conn, "shadow_signals", col, dtype)

    print("\n[SUCCESS] Shadow Instrument Migration Complete.")

if __name__ == "__main__":
    run_migration()
