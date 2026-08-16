import os
import sys
from sqlalchemy import create_engine, inspect
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv(os.path.join("backend", ".env"))

db_url = os.getenv("POSTGRES_URL")
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

def check():
    engine = create_engine(db_url)
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f"Tables in Neon: {tables}")

    if "live_signals" in tables:
        with engine.connect() as conn:
            from sqlalchemy import text
            res = conn.execute(text("SELECT count(*) FROM live_signals")).scalar()
            print(f"Count in live_signals: {res}")
    else:
        print("Table live_signals MISSING!")

if __name__ == "__main__":
    check()
