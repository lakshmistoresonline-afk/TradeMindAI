import os
import sys
from sqlalchemy import create_engine, text

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

DATABASE_URL = os.getenv("POSTGRES_URL")

def main():
    if not DATABASE_URL:
        print("POSTGRES_URL not found.")
        return

    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        try:
            conn.execute(text("ALTER TABLE model_registry ADD COLUMN horizon VARCHAR(20) DEFAULT 'SWING';"))
            conn.execute(text("CREATE INDEX ix_model_registry_horizon ON model_registry (horizon);"))
            conn.commit()
            print("Migration successful: Added horizon column to model_registry.")
        except Exception as e:
            print(f"Migration error (might already exist): {e}")

if __name__ == "__main__":
    main()
