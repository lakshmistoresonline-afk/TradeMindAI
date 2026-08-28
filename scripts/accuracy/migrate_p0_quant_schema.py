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
        print("[*] Extending live_signals for P0 Quantitative Intelligence...")
        # Add P0 columns
        columns = [
            ("raw_probability", "FLOAT"),
            ("calibrated_probability", "FLOAT"),
            ("expected_value", "FLOAT"),
            ("regime", "VARCHAR(50)"),
            ("regime_probability", "FLOAT"),
            ("risk_reward", "FLOAT"),
            ("risk_per_unit", "FLOAT"),
            ("reward_per_unit", "FLOAT"),
            ("data_quality_score", "FLOAT"),
            ("feature_snapshot_id", "VARCHAR(100)"),
            ("provenance", "TEXT") # JSONB preferred if native but using TEXT for SQLite compatibility
        ]

        for col_name, col_type in columns:
            try:
                conn.execute(text(f"ALTER TABLE live_signals ADD COLUMN IF NOT EXISTS {col_name} {col_type}"))
                print(f"   [+] Added {col_name}")
            except Exception as e:
                print(f"   [!] Skipping {col_name}: {e}")

        conn.commit()
        print("\n[SUCCESS] P0 Schema Migration Complete.")

if __name__ == "__main__":
    migrate()
