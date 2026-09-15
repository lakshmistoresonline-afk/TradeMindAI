import os
import sqlalchemy
from sqlalchemy import text
from dotenv import load_dotenv

load_dotenv('backend/.env')
db_url = os.getenv("POSTGRES_URL")
engine = sqlalchemy.create_engine(db_url)

try:
    with engine.connect() as conn:
        # Try to select the column specifically
        conn.execute(text("SELECT quality_class FROM live_signals LIMIT 1"))
        print("Selection of quality_class succeeded.")
except Exception as e:
    print(f"Error: {e}")
finally:
    engine.dispose()
