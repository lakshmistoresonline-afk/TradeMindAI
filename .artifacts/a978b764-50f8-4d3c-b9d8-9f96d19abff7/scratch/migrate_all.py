import sys
import os
from sqlalchemy import text
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')

from backend.core.postgres import engine

def migrate_table(table_name, cols_to_add):
    with engine.connect() as conn:
        print(f"[*] Checking for missing columns in '{table_name}'...")
        res = conn.execute(text(f"PRAGMA table_info({table_name})"))
        existing_cols = {row[1] for row in res}

        for col, type_ in cols_to_add.items():
            if col not in existing_cols:
                print(f"   [+] Adding column {col}...")
                conn.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {col} {type_}"))
        conn.commit()

def run_migration():
    # 1. Stocks
    stocks_cols = {
        "ai_status": "STRING",
        "ai_last_error": "STRING",
        "ai_investment_score": "FLOAT",
        "ai_investment_grade": "STRING",
        "analysis": "STRING",
        "structured_consensus": "STRING",
        "options_data": "STRING",
        "financial_history": "STRING",
        "health_metrics": "STRING",
        "confidence_metrics": "STRING",
        "delivery_rate": "FLOAT",
        "options_pcr": "FLOAT",
        "sector_alpha": "FLOAT",
        "is_fno": "BOOLEAN",
        "lot_size": "INTEGER",
        "index_weight": "FLOAT",
        "index_membership": "STRING"
    }
    migrate_table("stocks", stocks_cols)

    # 2. Historical Prices
    price_cols = {
        "open_interest": "BIGINT",
        "source": "STRING"
    }
    migrate_table("historical_prices", price_cols)

    # 3. Predictions
    pred_cols = {
        "metadata_json": "STRING"
    }
    migrate_table("predictions", pred_cols)

    # 4. Live Signals
    sig_cols = {
        "asset_class": "VARCHAR(20)",
        "underlying_symbol": "VARCHAR(20)",
        "strike": "FLOAT",
        "option_type": "VARCHAR(10)",
        "expiry": "DATETIME",
        "lot_size": "INTEGER",
        "raw_probability": "FLOAT",
        "calibrated_probability": "FLOAT",
        "expected_value": "FLOAT",
        "regime": "STRING",
        "regime_probability": "FLOAT",
        "risk_reward": "FLOAT",
        "risk_per_unit": "FLOAT",
        "reward_per_unit": "FLOAT",
        "data_quality_score": "FLOAT",
        "feature_snapshot_id": "STRING",
        "provenance": "STRING",
        "validated_at": "DATETIME",
        "triggered_at": "DATETIME",
        "trigger_price": "FLOAT",
        "trigger_condition": "STRING",
        "outcome_date": "DATETIME",
        "profit_pct": "FLOAT",
        "outcome_price": "FLOAT",
        "mfe": "FLOAT",
        "mae": "FLOAT",
        "model_version": "STRING",
        "events": "STRING"
    }
    migrate_table("live_signals", sig_cols)

    print("[SUCCESS] All migrations complete.")

if __name__ == "__main__":
    migrate_all = run_migration()
