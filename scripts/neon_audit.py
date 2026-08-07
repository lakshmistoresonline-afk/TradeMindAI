import os
import sqlalchemy
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv('backend/.env')

def audit():
    url = os.getenv("POSTGRES_URL")
    if not url:
        print("❌ POSTGRES_URL not found in .env")
        return

    print(f"Connecting to: {url.split('@')[-1]}")
    engine = create_engine(url)

    with engine.connect() as conn:
        tables = ["stocks", "historical_prices", "market_regimes", "intel_reports", "predictions"]
        print("\n--- NEON CLOUD DATABASE AUDIT ---")
        for table in tables:
            try:
                res = conn.execute(text(f"SELECT count(*) FROM {table}"))
                count = res.scalar()
                print(f"[{table:.<20}] {count} records")
            except Exception as e:
                print(f"[{table:.<20}] ❌ ERROR: {e}")

if __name__ == "__main__":
    audit()
