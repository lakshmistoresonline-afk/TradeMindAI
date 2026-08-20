
import os
import sys
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')
os.environ["TRADEMIND_EXECUTION_MODE"] = "local"

from backend.core.postgres import SessionLocal, PriceDB

def debug():
    session = SessionLocal()
    symbol = "RELIANCE"
    print(f"--- DEBUG SESSION QUERY: {symbol} ---")
    try:
        res = session.query(PriceDB).filter(PriceDB.symbol == symbol).limit(5).all()
        print(f"Result type: {type(res)}")
        print(f"Result length: {len(res)}")
        for i, r in enumerate(res):
            print(f"[{i}] Type: {type(r)} | Value: {r}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    debug()
