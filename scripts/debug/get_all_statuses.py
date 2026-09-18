import os
import sqlalchemy
from sqlalchemy import text
from dotenv import load_dotenv

load_dotenv('backend/.env')
db_url = os.getenv('POSTGRES_URL')
engine = sqlalchemy.create_engine(db_url)

def get():
    with engine.connect() as conn:
        res_l = conn.execute(text("SELECT DISTINCT status FROM live_signals"))
        res_s = conn.execute(text("SELECT DISTINCT status FROM shadow_signals"))
        statuses = set([r[0] for r in res_l] + [r[0] for r in res_s])
        print("Canonical Statuses found in DB:")
        for s in sorted(list(statuses)):
            print(f"  - {s}")

if __name__ == "__main__":
    get()
