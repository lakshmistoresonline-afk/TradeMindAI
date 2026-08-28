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
    print("--- TRADEMIND AI: MASTER SCHEMA MIGRATION ---")

    with engine.connect() as conn:
        # 1. shadow_scan_diagnostics
        cols_diag = [
            ("provider_name", "VARCHAR"),
            ("provider_latency_ms", "INTEGER")
        ]

        # 2. shadow_signals
        cols_shadow = [
            ("asset_class", "VARCHAR(20) DEFAULT 'EQUITY'"),
            ("instrument_id", "VARCHAR"),
            ("instrument_type", "VARCHAR"),
            ("capital_allocation", "FLOAT"),
            ("risk_amount", "FLOAT"),
            ("quantity", "INTEGER"),
            ("outcome_verified", "BOOLEAN DEFAULT FALSE")
        ]

        # 3. Create daily_metrics if missing
        if "postgresql" in str(engine.url):
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS daily_metrics (
                    date DATE PRIMARY KEY,
                    universe_version VARCHAR,
                    signals_generated INTEGER,
                    signals_active INTEGER,
                    target_hits INTEGER,
                    stop_losses INTEGER,
                    timeouts INTEGER,
                    expired INTEGER,
                    cancelled INTEGER,
                    invalid_outcomes INTEGER,
                    gross_pnl FLOAT,
                    fees FLOAT,
                    slippage FLOAT,
                    net_pnl FLOAT,
                    virtual_equity FLOAT,
                    drawdown FLOAT,
                    exposure FLOAT,
                    provider_reliability_pct FLOAT,
                    avg_latency_ms INTEGER,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            conn.commit()

        print("[*] Migrating shadow_scan_diagnostics...")
        for col, dtype in cols_diag:
            add_column_if_not_exists(conn, "shadow_scan_diagnostics", col, dtype)

        print("[*] Migrating shadow_signals...")
        for col, dtype in cols_shadow:
            add_column_if_not_exists(conn, "shadow_signals", col, dtype)

    print("\n[SUCCESS] Master Migration Complete.")

if __name__ == "__main__":
    run_migration()
