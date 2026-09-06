import os
import sys
from sqlalchemy import text
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')

from backend.core.postgres import engine

def run_fix():
    print("--- TRADEMIND AI: FIXING PREDICTIONS ID TYPE ---")

    with engine.connect() as conn:
        try:
            # 1. Drop existing primary key and index
            conn.execute(text("ALTER TABLE predictions DROP CONSTRAINT IF EXISTS predictions_pkey CASCADE"))

            # 2. Change column type
            conn.execute(text("ALTER TABLE predictions ALTER COLUMN id TYPE VARCHAR(50)"))

            # 3. Restore primary key
            conn.execute(text("ALTER TABLE predictions ADD PRIMARY KEY (id)"))

            # 4. Re-create index if needed (though PK creates one)
            conn.execute(text("CREATE INDEX IF NOT EXISTS ix_predictions_id ON predictions (id)"))

            conn.commit()
            print("[SUCCESS] Predictions table ID type fixed to VARCHAR.")
        except Exception as e:
            print(f"[FAILED] Error: {e}")
            conn.rollback()

if __name__ == "__main__":
    run_fix()
