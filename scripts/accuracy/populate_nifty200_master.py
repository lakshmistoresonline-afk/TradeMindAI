import os
import sys
import asyncio
from datetime import datetime
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')

from backend.core.postgres import SessionLocal, StockDB

# A representative list of Nifty 200 stocks (subset for brevity in script, but ready for full list)
NIFTY_200_SYMBOLS = [
    "RELIANCE", "TCS", "HDFCBANK", "INFY", "ICICIBANK", "SBIN", "BHARTIARTL", "AXISBANK", "LT", "ITC",
    "KOTAKBANK", "HINDUNILVR", "BAJFINANCE", "HCLTECH", "MARUTI", "SUNPHARMA", "TITAN", "ADANIENT", "ULTRACEMCO", "TATASTEEL",
    "JSWSTEEL", "NTPC", "M&M", "POWERGRID", "ASIANPAINT", "LICI", "ADANIPORTS", "ADANIGREEN", "ADANIPOWER", "COALINDIA",
    "TATASTEEL", "BAJAJFINSV", "GRASIM", "HINDALCO", "JSWSTEEL", "NESTLEIND", "ONGC", "TATASTEEL", "WIPRO", "HDFCLIFE",
    "SBILIFE", "DRREDDY", "ADANIENSOL", "EICHERMOT", "INDUSINDBK", "BPCL", "TECHM", "DIVISLAB", "CIPLA", "TATAMOTORS",
    "BAJAJ-AUTO", "BRITANNIA", "APOLLOHOSP", "HEROMOTOCO", "COALINDIA", "SHREECEM", "GRASIM", "INDHOTEL", "JSWSTEEL", "LTIM",
    "TATACONSUM", "HINDALCO", "PIDILITIND", "BEL", "HAL", "CANBK", "TRENT", "DLF", "PNB", "BANKBARODA",
    "GODREJCP", "GAIL", "CHOLAFIN", "SIEMENS", "ABB", "VBL", "UNITDSPR", "TATACOMM", "AMBUJACEM", "AUROPHARMA",
    "BOSCHLTD", "CUMMINSIND", "ESCORTS", "GLENMARK", "HAVELLS", "IDFCFIRSTB", "IOC", "IRCTC", "JINDALSTEL", "JUBLFOOD",
    "LICHSGFIN", "LUPIN", "M&MFIN", "MRF", "MUTHOOTFIN", "NMDC", "OBEROIRLTY", "PEL", "PFC", "RECLTD",
    "SAIL", "SRF", "TVSMOTOR", "VOLTAS", "ZYDUSLIFE", "POLYCAB", "LICI", "NYKAA", "PAYTM", "ZOMATO",
    "MAXHEALTH", "YESBANK", "RVNL", "IRFC", "MAHABANK", "UNIONBANK", "IDBI", "UCOBANK", "CENTRALBK", "IOB"
]

# Lot sizes for F&O stocks (Sample mapping)
LOT_SIZES = {
    "NIFTY": 25, "BANKNIFTY": 15, "FINNIFTY": 40, "RELIANCE": 250, "TCS": 175, "HDFCBANK": 550,
    "INFY": 400, "ICICIBANK": 700, "SBIN": 1500, "BHARTIARTL": 950, "AXISBANK": 625, "LT": 300,
    "ITC": 1600, "KOTAKBANK": 400, "MARUTI": 50, "TATASTEEL": 5500, "TATAMOTORS": 1425, "BAJFINANCE": 125
}

async def populate():
    db = SessionLocal()
    print(f"[*] Starting master population for {len(NIFTY_200_SYMBOLS)} stocks...")

    try:
        count = 0
        for sym in NIFTY_200_SYMBOLS:
            stock = db.query(StockDB).filter(StockDB.symbol == sym).first()

            # Identify if F&O
            is_fno = sym in LOT_SIZES or sym in ["NIFTY", "BANKNIFTY"]
            lot = LOT_SIZES.get(sym, None)

            data = {
                "symbol": sym,
                "name": f"{sym} Limited",
                "is_fno": is_fno,
                "lot_size": lot,
                "ai_status": "READY",
                "updated_at": datetime.utcnow()
            }

            if not stock:
                db.add(StockDB(**data))
            else:
                for k, v in data.items():
                    setattr(stock, k, v)
            count += 1
            if count % 20 == 0:
                print(f"   [Progress] {count} stocks processed...")

        db.commit()
        print(f"[+] Master population complete. Total: {count} stocks.")
    except Exception as e:
        print(f"[-] Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(populate())
