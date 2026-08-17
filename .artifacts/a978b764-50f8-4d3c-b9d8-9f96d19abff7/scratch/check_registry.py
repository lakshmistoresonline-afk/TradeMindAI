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
        res = conn.execute(text("SELECT name, symbol, version, accuracy, hyperparameters, calibration_metadata FROM model_registry WHERE is_champion = 1"))
        print("--- Champion Models ---")
        for r in res:
            hp = json.loads(r[4]) if isinstance(r[4], str) else r[4]
            print(f"{r[1]} | {r[0]} | Acc: {r[3]} | Features: {hp.get('feature_names')}")

if __name__ == "__main__":
    check()
