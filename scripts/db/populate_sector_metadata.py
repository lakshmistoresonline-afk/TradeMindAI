import os
import sqlalchemy
from sqlalchemy import text
from dotenv import load_dotenv

load_dotenv('backend/.env')
db_url = os.getenv('POSTGRES_URL')
engine = sqlalchemy.create_engine(db_url)

SECTOR_MAP = {
    "ACC": "CEMENT",
    "AMBUJACEM": "CEMENT",
    "ABB": "CAPITAL GOODS",
    "BAJFINANCE": "FINANCIAL SERVICES",
    "CANFINHOME": "FINANCIAL SERVICES",
    "APOLLOTYRE": "AUTO",
    "ADANIENT": "METALS & MINING",
    "RELIANCE": "ENERGY",
    "TCS": "IT",
    "INFY": "IT",
    "ICICIBANK": "FINANCIAL SERVICES",
    "AXISBANK": "FINANCIAL SERVICES",
    "SBIN": "FINANCIAL SERVICES",
    "HDFCBANK": "FINANCIAL SERVICES",
    "LT": "CONSTRUCTION",
    "ITC": "CONSUMER GOODS",
    "HINDUNILVR": "CONSUMER GOODS",
    "BHARTIARTL": "TELECOM",
    "KOTAKBANK": "FINANCIAL SERVICES",
    "MARUTI": "AUTO",
    "TATASTEEL": "METALS & MINING",
    "SUNPHARMA": "PHARMA",
    "CIPLA": "PHARMA",
    "DRREDDY": "PHARMA",
    "BRITANNIA": "CONSUMER GOODS",
    "TITAN": "CONSUMER GOODS",
    "ADANIPORTS": "SERVICES",
    "ULTRACEMCO": "CEMENT",
    "JSWSTEEL": "METALS & MINING",
    "GRASIM": "CEMENT",
    "POWERGRID": "ENERGY",
    "NTPC": "ENERGY",
    "ONGC": "ENERGY",
    "COALINDIA": "ENERGY",
    "M&M": "AUTO",
    "BAJAJ-AUTO": "AUTO",
    "HINDALCO": "METALS & MINING"
}

def populate():
    with engine.connect() as conn:
        print("[*] Populating sector metadata...")
        for sym, sector in SECTOR_MAP.items():
            res = conn.execute(text(f"UPDATE stocks SET sector = '{sector}' WHERE symbol = '{sym}'"))
            if res.rowcount > 0:
                print(f"   Updated {sym} -> {sector}")

        conn.commit()
        print("[+] Migration successful.")

if __name__ == "__main__":
    populate()
