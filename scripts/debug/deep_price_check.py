import os
import sqlalchemy
from sqlalchemy import text
from dotenv import load_dotenv

load_dotenv('backend/.env')
db_url = os.getenv('POSTGRES_URL')
engine = sqlalchemy.create_engine(db_url)

def audit():
    with engine.connect() as conn:
        print("--- DEEP PRICE AUDIT ---")

        # 1. Fetch signal IDs from live_signals
        res = conn.execute(text("SELECT id, symbol, entry_price, current_price FROM live_signals LIMIT 5"))
        for row in res:
            sid, sym, entry, current = row
            print(f"\nLiveSignal: {sid} ({sym})")
            print(f"   Entry: {entry}")
            print(f"   Current: {current}")

            # 2. Check if same ID exists in shadow_signals
            res_s = conn.execute(text(f"SELECT entry_price, current_price FROM shadow_signals WHERE id = '{sid}'"))
            row_s = res_s.fetchone()
            if row_s:
                print(f"   ShadowSignal (SAME ID): Entry {row_s[0]} | Current {row_s[1]}")
            else:
                print(f"   ShadowSignal: NOT FOUND")

if __name__ == "__main__":
    audit()
