import os
import sqlalchemy
from sqlalchemy import text
from dotenv import load_dotenv

# Load env from backend/.env
load_dotenv('backend/.env')

db_url = os.getenv("POSTGRES_URL")
if not db_url:
    print("No POSTGRES_URL found in env")
    exit(1)

print(f"Connecting to: {db_url[:50]}...")
engine = sqlalchemy.create_engine(db_url)
try:
    with engine.connect() as conn:
        res = conn.execute(text("SELECT COUNT(*) FROM live_signals"))
        count = res.scalar()
        print(f"Total signals in Neon live_signals table: {count}")

        res = conn.execute(text("SELECT timeframe, COUNT(*) FROM live_signals GROUP BY timeframe"))
        for row in res:
            print(f"   {row[0]}: {row[1]}")
except Exception as e:
    print(f"Error: {e}")
finally:
    engine.dispose()
