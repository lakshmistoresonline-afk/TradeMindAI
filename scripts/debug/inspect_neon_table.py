import os
import sqlalchemy
from sqlalchemy import text
from dotenv import load_dotenv

# Load env from backend/.env
load_dotenv('backend/.env')

db_url = os.getenv("POSTGRES_URL")
engine = sqlalchemy.create_engine(db_url)
try:
    with engine.connect() as conn:
        res = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'stocks'"))
        cols = [row[0] for row in res]
        print(f"Columns in stocks: {cols}")
        if "quality_class" in cols:
            print("   [OK] quality_class exists.")
        else:
            print("   [FAIL] quality_class MISSING.")
except Exception as e:
    print(f"Error: {e}")
finally:
    engine.dispose()
