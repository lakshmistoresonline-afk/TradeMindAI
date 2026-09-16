import os
import sqlalchemy
from sqlalchemy import text
from dotenv import load_dotenv

load_dotenv('backend/.env')
db_url = os.getenv('POSTGRES_URL')
engine = sqlalchemy.create_engine(db_url)

with engine.connect() as conn:
    print("--- live_signals columns ---")
    res = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'live_signals'"))
    for row in res:
        print(row[0])

    print("\n--- Sample Record ---")
    res2 = conn.execute(text("SELECT * FROM live_signals LIMIT 1"))
    row = res2.fetchone()
    if row:
        # Get column names from result
        cols = res2.keys()
        for i, val in enumerate(row):
            print(f"{cols[i]}: {val}")
