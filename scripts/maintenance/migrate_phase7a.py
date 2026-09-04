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
    print("--- TRADEMIND AI: PHASE 7A SCHEMA MIGRATION ---")

    with engine.connect() as conn:
        # 1. stocks table
        cols_stocks = [
            ("universe_version", "VARCHAR DEFAULT 'NIFTY_200_AUG2026'"),
            ("data_freshness_status", "VARCHAR"),
            ("missing_data_reason", "VARCHAR"),
            ("ingestion_timestamp", "TIMESTAMP")
        ]

        # 2. predictions table (Transform if needed, or just add new columns)
        # Note: id was Integer, now String in model.
        # In SQL, we usually don't change PK type easily.
        # Let's see if we should create a new table or just add columns.
        # specification says "Every prediction must be persistable".
        # If it's Postgres, we can add columns.
        cols_predictions = [
            ("feature_version", "VARCHAR"),
            ("probability", "FLOAT"),
            ("expected_value", "FLOAT"),
            ("direction", "VARCHAR"),
            ("regime", "VARCHAR"),
            ("created_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
        ]

        # 3. live_signals / shadow_signals
        cols_signals = [
            ("prediction_id", "VARCHAR"),
            ("provenance_id", "VARCHAR")
        ]

        print("[*] Migrating stocks...")
        for col, dtype in cols_stocks:
            add_column_if_not_exists(conn, "stocks", col, dtype)

        print("[*] Migrating predictions (Existing columns only)...")
        # Rename date to timestamp if it's Postgres and exists
        if "postgresql" in str(engine.url):
             try:
                 conn.execute(text("ALTER TABLE predictions RENAME COLUMN date TO timestamp"))
                 conn.commit()
                 print("   [+] Renamed date to timestamp in predictions.")
             except: pass

        for col, dtype in cols_predictions:
            add_column_if_not_exists(conn, "predictions", col, dtype)

        print("[*] Migrating live_signals...")
        for col, dtype in cols_signals:
            add_column_if_not_exists(conn, "live_signals", col, dtype)

        print("[*] Migrating shadow_signals...")
        for col, dtype in cols_signals:
            add_column_if_not_exists(conn, "shadow_signals", col, dtype)

    print("\n[SUCCESS] Phase 7A Migration Complete.")

if __name__ == "__main__":
    run_migration()
