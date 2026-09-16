import os
import sqlalchemy
from sqlalchemy import text
from dotenv import load_dotenv

load_dotenv('backend/.env')
db_url = os.getenv('POSTGRES_URL')
engine = sqlalchemy.create_engine(db_url)

def audit():
    with engine.connect() as conn:
        print("--- TIMESTAMP FORENSICS ---")

        # Check a sample of 10 signals
        res = conn.execute(text("SELECT id, symbol, timestamp, data_timestamp, created_at FROM shadow_signals LIMIT 10"))
        for row in res:
            sid, sym, ts, data_ts, created = row
            # ts and data_ts can be None in some records, let's see
            valid = "PASS"
            if data_ts and ts and data_ts > ts: valid = "FAIL (Look-ahead)"
            print(f"Signal {sid} ({sym}): Decision: {ts}, Data: {data_ts}, Created: {created} -> {valid}")

        print("\n--- Market Data Check ---")
        res2 = conn.execute(text("SELECT symbol, COUNT(*), MIN(date), MAX(date) FROM historical_prices GROUP BY symbol LIMIT 5"))
        for row in res2:
            print(f"Symbol {row[0]}: {row[1]} bars, {row[2]} to {row[3]}")

if __name__ == "__main__":
    audit()
