import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

load_dotenv('backend/.env')

def sync_schema():
    url = os.getenv("POSTGRES_URL")
    engine = create_engine(url)

    with engine.connect() as conn:
        print("Cleaning up old schema...")
        conn.execute(text("DROP TABLE IF EXISTS market_regimes"))
        conn.execute(text("DROP TABLE IF EXISTS intel_reports"))
        conn.commit()

    from backend.core.postgres import init_db
    init_db()
    print("Schema Re-synchronized Successfully.")

if __name__ == "__main__":
    sync_schema()
    # (Removed inspect call temporarily)
