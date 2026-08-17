import sys
import os
from sqlalchemy import text
from dotenv import load_dotenv
import pandas as pd
import json

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')

from backend.core.postgres import engine

def check():
    with engine.connect() as conn:
        res = conn.execute(text("SELECT symbol, raw_probability, calibrated_probability FROM live_signals WHERE symbol = 'RELIANCE' LIMIT 10"))
        print("--- Live Signals ---")
        print(res.fetchall())

        res = conn.execute(text("SELECT symbol, confidence, metadata_json FROM predictions WHERE symbol = 'RELIANCE' LIMIT 10"))
        print("\n--- Predictions ---")
        for r in res:
            print(f"{r[0]} | {r[1]} | {r[2]}")

if __name__ == "__main__":
    check()
