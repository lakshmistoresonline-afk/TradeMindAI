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
        res = conn.execute(text("SELECT symbol, direction, decision_timestamp, calibrated_probability FROM live_signals ORDER BY symbol, decision_timestamp;"))
        rows = res.fetchall()
        print(f"Total signals: {len(rows)}")
        for r in rows:
            print(r)

if __name__ == "__main__":
    main()
