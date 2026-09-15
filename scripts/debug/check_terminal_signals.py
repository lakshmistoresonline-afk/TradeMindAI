import os
import sqlalchemy
from sqlalchemy import text
from dotenv import load_dotenv

load_dotenv('backend/.env')
db_url = os.getenv('POSTGRES_URL')
engine = sqlalchemy.create_engine(db_url)

with engine.connect() as conn:
    print("--- live_signals ---")
    res = conn.execute(text("SELECT status, COUNT(*) FROM live_signals GROUP BY status"))
    for row in res:
        print(f"{row[0]}: {row[1]}")

    print("\n--- shadow_signals ---")
    res = conn.execute(text("SELECT status, COUNT(*) FROM shadow_signals GROUP BY status"))
    for row in res:
        print(f"{row[0]}: {row[1]}")
