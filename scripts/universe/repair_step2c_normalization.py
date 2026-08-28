import os
import sys
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')

from backend.core.postgres import SessionLocal, LiveSignalDB

def repair():
    db = SessionLocal()
    print("[*] Applying Price Normalization Factors (Step 2C)...")

    sigs = db.query(LiveSignalDB).filter(LiveSignalDB.id.like('master_%')).all()

    factors = {
        "RELIANCE": 2.31,
        "INFY": 1.72,
        "ITC": 1.84,
        "TCS": 2.00,
        "LT": 0.88 # 3550 / 4042
    }

    for s in sigs:
        factor = factors.get(s.symbol, 1.0)
        s.price_adjustment_factor = factor
        print(f"   [+] {s.symbol:<12} | Factor: {factor}")

    db.commit()
    db.close()
    print("\n[SUCCESS] Normalization Factors Applied.")

if __name__ == "__main__":
    repair()
