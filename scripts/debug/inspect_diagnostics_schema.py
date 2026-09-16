import os
import sqlalchemy
from sqlalchemy import text
from dotenv import load_dotenv

load_dotenv('backend/.env')
db_url = os.getenv('POSTGRES_URL')
engine = sqlalchemy.create_engine(db_url)

with engine.connect() as conn:
    print("--- shadow_scan_diagnostics columns ---")
    res = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'shadow_scan_diagnostics'"))
    for row in res:
        print(row[0])
