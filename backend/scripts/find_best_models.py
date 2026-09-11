import os
import sys
from sqlalchemy import create_engine, text

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DATABASE_URL = os.getenv("POSTGRES_URL")

def main():
    if not DATABASE_URL:
        print("POSTGRES_URL not found.")
        return

    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        print("--- BEST CHAMPION MODELS ---")
        res = conn.execute(text("SELECT symbol, accuracy, roc_auc FROM model_registry WHERE is_champion=True ORDER BY roc_auc DESC LIMIT 20;"))
        rows = res.fetchall()
        for r in rows:
            print(r)

if __name__ == "__main__":
    main()
