import os
import sys
from sqlalchemy import text
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')

from backend.core.postgres import engine, Base

def run_schema_upgrade():
    print("--- TRADEMIND AI: APPLYING LEDGER 2.0 SCHEMA UPGRADE ---")

    # Use Base.metadata.create_all to create new tables (signal_corrections, shadow_provenance)
    Base.metadata.create_all(bind=engine)
    print("[*] New tables created.")

    # Add columns to existing shadow_signals table
    # This is a safe way to add columns to Postgres
    columns_to_add = [
        ("asset_type", "VARCHAR(20)"),
        ("exchange", "VARCHAR(10)"),
        ("underlying_symbol", "VARCHAR(20)"),
        ("signal_type", "VARCHAR(20)"),
        ("signal_rating", "VARCHAR(10)"),
        ("conviction", "FLOAT"),
        ("entry_zone_low", "FLOAT"),
        ("entry_zone_high", "FLOAT"),
        ("current_price", "FLOAT"),
        ("price_timestamp", "TIMESTAMP"),
        ("derivative_symbol", "VARCHAR(50)"),
        ("contract_multiplier", "INTEGER"),
        ("derivative_entry", "FLOAT"),
        ("derivative_current", "FLOAT"),
        ("derivative_target", "FLOAT"),
        ("derivative_stop", "FLOAT"),
        ("premium_timestamp", "TIMESTAMP"),
        ("signal_timestamp", "TIMESTAMP"),
        ("last_updated_at", "TIMESTAMP"),
        ("entry_timestamp", "TIMESTAMP"),
        ("exit_timestamp", "TIMESTAMP"),
        ("lifecycle_state", "VARCHAR(30)"),
        ("outcome_status", "VARCHAR(30)"),
        ("verification_level", "INTEGER"),
        ("risk_amount_abs", "FLOAT"),
        ("reward_amount_abs", "FLOAT"),
        ("expected_return", "FLOAT"),
        ("feature_snapshot_id", "VARCHAR"),
        ("market_snapshot_id", "VARCHAR"),
        ("model_run_id", "VARCHAR"),
        ("decision_id", "VARCHAR"),
        ("created_by", "VARCHAR"),
        ("calculation_version", "VARCHAR"),
        ("pnl_engine_version", "VARCHAR"),
        ("outcome_engine_version", "VARCHAR"),
        ("reconstruction_version", "VARCHAR"),
        ("last_reconciled_at", "TIMESTAMP"),
        ("record_hash", "VARCHAR"),
        ("audit_status", "VARCHAR")
    ]

    with engine.connect() as conn:
        for col_name, col_type in columns_to_add:
            try:
                conn.execute(text(f"ALTER TABLE shadow_signals ADD COLUMN {col_name} {col_type}"))
                print(f"  [+] Column added: {col_name}")
            except Exception as e:
                # Column likely already exists
                print(f"  [!] Skipping {col_name}: {e}")
        conn.commit()

    print("\n[SUCCESS] Schema upgrade complete.")

if __name__ == "__main__":
    run_schema_upgrade()
