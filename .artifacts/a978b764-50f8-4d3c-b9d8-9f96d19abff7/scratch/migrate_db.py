import sys
import os
from sqlalchemy import text
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')

from backend.core.postgres import engine

def migrate():
    with engine.connect() as conn:
        print("[*] Checking for missing columns in 'stocks'...")
        cols_to_add = {
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

        # Get existing columns
        res = conn.execute(text("PRAGMA table_info(stocks)"))
        existing_cols = {row[1] for row in res}

        for col, type_ in cols_to_add.items():
            if col not in existing_cols:
                print(f"   [+] Adding column {col}...")
                conn.execute(text(f"ALTER TABLE stocks ADD COLUMN {col} {type_}"))

        conn.commit()
        print("[SUCCESS] Migration complete.")

if __name__ == "__main__":
    migrate()
