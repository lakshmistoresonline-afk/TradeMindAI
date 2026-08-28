import os
import sys
from sqlalchemy import text, inspect
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load backend environment variables
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend", ".env"))

from backend.core.postgres import engine

def check():
    with engine.connect() as conn:
        tables = ["opportunities", "trade_journal", "predictions"]
        for t in tables:
            try:
                count = conn.execute(text(f"SELECT count(*) FROM {t}")).scalar()
                print(f"{t.capitalize()}: {count}")
                if t == "opportunities":
                    null_ts = conn.execute(text("SELECT count(*) FROM opportunities WHERE timestamp IS NULL")).scalar()
                    print(f"   Null Timestamps: {null_ts}")
            except Exception as e:
                print(f"{t.capitalize()}: ERROR ({e})")

        print("\n--- Columns ---")
        inspector = inspect(engine)
        for t in tables:
            try:
                cols = [c["name"] for c in inspector.get_columns(t)]
                print(f"{t.capitalize()}: {cols}")
            except:
                print(f"{t.capitalize()}: Table not found")

if __name__ == "__main__":
    check()
