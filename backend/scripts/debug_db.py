import os
import sys
from sqlalchemy import create_engine, text

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DATABASE_URL = os.getenv("POSTGRES_URL")

def check_models():
    if not DATABASE_URL:
        print("POSTGRES_URL not found.")
        return

    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        print("--- MODEL REGISTRY ---")
        res = conn.execute(text("SELECT symbol, version, is_champion, status FROM model_registry;"))
        rows = res.fetchall()
        print(f"Total entries: {len(rows)}")
        champions = [r for r in rows if r[2]]
        print(f"Champions: {len(champions)}")
        for r in rows[:10]:
            print(r)

        print("\n--- STOCKS ---")
        res = conn.execute(text("SELECT count(*) FROM stocks;"))
        print(f"Total stocks: {res.scalar()}")

        print("\n--- MODEL HORIZONS ---")
        res = conn.execute(text("SELECT horizon, count(*) FROM model_registry GROUP BY horizon;"))
        for r in res.fetchall():
            print(r)

        res = conn.execute(text("SELECT symbol, horizon, is_champion FROM model_registry WHERE is_champion=True LIMIT 20;"))
        for r in res.fetchall():
            print(r)

if __name__ == "__main__":
    check_models()
