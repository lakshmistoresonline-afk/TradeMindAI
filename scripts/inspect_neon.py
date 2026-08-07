import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv('backend/.env')

def inspect():
    url = os.getenv("POSTGRES_URL")
    engine = create_engine(url)

    with engine.connect() as conn:
        print("\n--- intel_reports ---")
        res = conn.execute(text("SELECT id, type, date, summary FROM intel_reports"))
        for row in res:
            print(row)

        print("\n--- stocks ---")
        res = conn.execute(text("SELECT symbol, updated_at FROM stocks"))
        for row in res:
            print(row)

if __name__ == "__main__":
    inspect()
