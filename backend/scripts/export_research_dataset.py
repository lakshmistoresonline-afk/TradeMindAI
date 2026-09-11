import os
import sys
import pandas as pd
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
        res = conn.execute(text("SELECT * FROM live_signals;"))
        df = pd.DataFrame(res.fetchall(), columns=res.keys())

        os.makedirs("reports", exist_ok=True)
        df.to_csv("reports/V22_CANONICAL_RESEARCH_DATASET.csv", index=False)
        print(f"Exported {len(df)} signals to reports/V22_CANONICAL_RESEARCH_DATASET.csv")

if __name__ == "__main__":
    main()
