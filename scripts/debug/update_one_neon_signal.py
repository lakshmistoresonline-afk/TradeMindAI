import os
import sqlalchemy
from sqlalchemy import text
from dotenv import load_dotenv

load_dotenv('backend/.env')
db_url = os.getenv("POSTGRES_URL")
engine = sqlalchemy.create_engine(db_url)

try:
    with engine.connect() as conn:
        res = conn.execute(text("UPDATE live_signals SET quality_class = 'PRIMARY' WHERE id = (SELECT id FROM live_signals LIMIT 1) RETURNING id"))
        updated_id = res.scalar()
        conn.commit()
        print(f"Updated signal {updated_id} to PRIMARY in Neon.")
except Exception as e:
    print(f"Error: {e}")
finally:
    engine.dispose()
