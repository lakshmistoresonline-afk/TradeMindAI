
import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')

def check():
    pg_url = os.getenv("POSTGRES_URL")
    engine = create_engine(pg_url)
    with engine.connect() as conn:
        res = conn.execute(text("SELECT event_type, count(*) FROM shadow_events GROUP BY event_type")).fetchall()
        for r in res:
            print(f"{r[0]}: {r[1]}")

if __name__ == "__main__":
    check()
