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
    print("--- TRADEMIND AI: STEP 3A SCHEMA MIGRATION ---")

    with engine.connect() as conn:
        # 1. live_signals additions
        cols_live = [
            ("universe_version", "VARCHAR"),
            ("strategy_version", "VARCHAR DEFAULT 'v2.2'"),
            ("data_timestamp", "TIMESTAMP"),
            ("market_timestamp", "TIMESTAMP"),
            ("evaluation_mode", "VARCHAR DEFAULT 'LIVE_SHADOW'"),
            ("exit_reason", "VARCHAR"),
            ("fees", "FLOAT"),
            ("slippage", "FLOAT"),
            ("net_pnl", "FLOAT"),
            ("signal_eligibility", "VARCHAR")
        ]

        # 2. shadow_signals additions
        cols_shadow = [
            ("universe_version", "VARCHAR DEFAULT 'NIFTY_200_AUG2026'"),
            ("data_timestamp", "TIMESTAMP"),
            ("market_timestamp", "TIMESTAMP"),
            ("evaluation_mode", "VARCHAR DEFAULT 'LIVE_SHADOW'"),
            ("exit_reason", "VARCHAR"),
            ("signal_eligibility", "VARCHAR")
        ]

        # 3. shadow_events additions
        cols_events = [
            ("evaluation_mode", "VARCHAR DEFAULT 'LIVE_SHADOW'")
        ]

        print("[*] Migrating live_signals...")
        for col, dtype in cols_live:
            add_column_if_not_exists(conn, "live_signals", col, dtype)

        print("[*] Migrating shadow_signals...")
        for col, dtype in cols_shadow:
            add_column_if_not_exists(conn, "shadow_signals", col, dtype)

        print("[*] Migrating shadow_events...")
        for col, dtype in cols_events:
            add_column_if_not_exists(conn, "shadow_events", col, dtype)

    print("\n[SUCCESS] Step 3A Migration Complete.")

if __name__ == "__main__":
    run_migration()
