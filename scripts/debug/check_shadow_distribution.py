import os
import sqlalchemy
from sqlalchemy import text
from dotenv import load_dotenv

load_dotenv('backend/.env')
db_url = os.getenv('POSTGRES_URL')
engine = sqlalchemy.create_engine(db_url)

with engine.connect() as conn:
    print("--- shadow_signals: signal_type distribution (Closed) ---")
    res = conn.execute(text("SELECT signal_type, COUNT(*) FROM shadow_signals WHERE status != 'ACTIVE' GROUP BY signal_type"))
    for row in res: print(f"{row[0]} : {row[1]}")

    print("\n--- shadow_signals: total history count ---")
    res = conn.execute(text("SELECT COUNT(*) FROM shadow_signals WHERE status != 'ACTIVE'"))
    print(f"Total: {res.scalar()}")
