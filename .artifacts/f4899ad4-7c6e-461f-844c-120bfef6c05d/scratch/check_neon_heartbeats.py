
import os
import sys
import json
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')

def check():
    pg_url = os.getenv("POSTGRES_URL")
    if not pg_url:
        print("POSTGRES_URL not found")
        return

    engine = create_engine(pg_url)
    with engine.connect() as conn:
        print("--- NEON HEARTBEAT AUDIT ---")
        query = text("SELECT id, timestamp, decision, payload_json FROM shadow_events WHERE event_type = 'HEARTBEAT' ORDER BY timestamp DESC LIMIT 10")
        rows = conn.execute(query).fetchall()
        if not rows:
            print("No heartbeats found.")
        else:
            for r in rows:
                print(f"ID: {r[0]} | TS: {r[1]} | Status: {r[2]} | Payload: {r[3]}")

if __name__ == "__main__":
    check()
