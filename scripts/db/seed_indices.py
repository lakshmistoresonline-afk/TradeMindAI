import os
import sqlalchemy
from sqlalchemy import text
from dotenv import load_dotenv

load_dotenv('backend/.env')
db_url = os.getenv('POSTGRES_URL')
engine = sqlalchemy.create_engine(db_url)

INDICES = [
    {"symbol": "NIFTY", "name": "NIFTY 50", "sector": "INDEX"},
    {"symbol": "BANKNIFTY", "name": "BANK NIFTY", "sector": "INDEX"},
    {"symbol": "INDIAVIX", "name": "India VIX", "sector": "INDEX"}
]

def seed():
    with engine.connect() as conn:
        print("[*] Seeding indices into stocks table...")
        for idx in INDICES:
            res = conn.execute(text(f"SELECT COUNT(*) FROM stocks WHERE symbol = '{idx['symbol']}'"))
            if res.scalar() == 0:
                conn.execute(text(f"INSERT INTO stocks (symbol, name, sector, index_membership) VALUES ('{idx['symbol']}', '{idx['name']}', '{idx['sector']}', 'INDEX')"))
                print(f"   Inserted {idx['symbol']}")
            else:
                print(f"   {idx['symbol']} already exists.")

        conn.commit()
        print("[+] Seeding complete.")

if __name__ == "__main__":
    seed()
