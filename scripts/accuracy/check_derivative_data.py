import os
import sys
from sqlalchemy import text, create_engine
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
load_dotenv('backend/.env')

from backend.core.postgres import engine

def check_data():
    with engine.connect() as conn:
        print("[*] Checking signal counts by asset_class...")
        res = conn.execute(text("SELECT asset_class, count(*) FROM live_signals GROUP BY asset_class"))
        for row in res:
            print(f"   Asset Class: {row[0]}, Count: {row[1]}")

        print("\n[*] Sampling derivative signals if any...")
        res = conn.execute(text("SELECT id, symbol, asset_class, status FROM live_signals WHERE asset_class IN ('FUTURES', 'OPTIONS') LIMIT 5"))
        for row in res:
            print(f"   ID: {row[0]}, Symbol: {row[1]}, Class: {row[2]}, Status: {row[3]}")

if __name__ == "__main__":
    check_data()
