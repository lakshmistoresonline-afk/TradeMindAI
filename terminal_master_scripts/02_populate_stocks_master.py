import os
import sys
import asyncio
from datetime import datetime
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')

from backend.core.postgres import SessionLocal, StockDB

# Nifty 200 constituents + Indices
NIFTY_200_SYMBOLS = [
    "NIFTY", "BANKNIFTY", "RELIANCE", "TCS", "HDFCBANK", "INFY", "ICICIBANK", "SBIN", "BHARTIARTL", "AXISBANK", "LT", "ITC",
    "KOTAKBANK", "HINDUNILVR", "BAJFINANCE", "HCLTECH", "MARUTI", "SUNPHARMA", "TITAN", "ADANIENT", "ULTRACEMCO", "TATASTEEL",
    "JSWSTEEL", "NTPC", "M&M", "POWERGRID", "ASIANPAINT", "LICI", "ADANIPORTS", "ADANIGREEN", "ADANIPOWER", "COALINDIA",
    "BAJAJFINSV", "GRASIM", "HINDALCO", "NESTLEIND", "ONGC", "WIPRO", "HDFCLIFE", "SBILIFE", "DRREDDY", "ADANIENSOL",
    "EICHERMOT", "INDUSINDBK", "BPCL", "TECHM", "DIVISLAB", "CIPLA", "TATAMOTORS", "BAJAJ-AUTO", "BRITANNIA", "APOLLOHOSP",
    "HEROMOTOCO", "SHREECEM", "INDHOTEL", "LTIM", "TATACONSUM", "PIDILITIND", "BEL", "HAL", "CANBK", "TRENT",
    "DLF", "PNB", "BANKBARODA", "GODREJCP", "GAIL", "CHOLAFIN", "SIEMENS", "ABB", "VBL", "UNITDSPR",
    "TATACOMM", "AMBUJACEM", "AUROPHARMA", "BOSCHLTD", "CUMMINSIND", "ESCORTS", "GLENMARK", "HAVELLS", "IDFCFIRSTB", "IOC",
    "IRCTC", "JINDALSTEL", "JUBLFOOD", "LICHSGFIN", "LUPIN", "M&MFIN", "MRF", "MUTHOOTFIN", "NMDC", "OBEROIRLTY",
    "PEL", "PFC", "RECLTD", "SAIL", "SRF", "TVSMOTOR", "VOLTAS", "ZYDUSLIFE", "POLYCAB", "NYKAA",
    "PAYTM", "ZOMATO", "MAXHEALTH", "YESBANK", "RVNL", "IRFC", "MAHABANK", "UNIONBANK", "IDBI", "UCOBANK",
    "CENTRALBK", "IOB"
]

# Market Lot Sizes for major F&O symbols
LOT_SIZES = {
    "NIFTY": 25, "BANKNIFTY": 15, "FINNIFTY": 40, "RELIANCE": 250, "TCS": 175, "HDFCBANK": 550,
    "INFY": 400, "ICICIBANK": 700, "SBIN": 1500, "BHARTIARTL": 950, "AXISBANK": 625, "LT": 300,
    "ITC": 1600, "KOTAKBANK": 400, "MARUTI": 50, "TATASTEEL": 5500, "TATAMOTORS": 1425, "BAJFINANCE": 125
}

async def populate():
    db = SessionLocal()
    print(f"[*] STEP 2: Populating master table with {len(NIFTY_200_SYMBOLS)} stocks...")

    try:
        count = 0
        for sym in NIFTY_200_SYMBOLS:
            stock = db.query(StockDB).filter(StockDB.symbol == sym).first()

            is_fno = sym in LOT_SIZES or sym in ["NIFTY", "BANKNIFTY"]
            lot = LOT_SIZES.get(sym, None)

            data = {
                "symbol": sym,
                "name": f"{sym} Index" if sym in ["NIFTY", "BANKNIFTY"] else f"{sym} Limited",
                "is_fno": is_fno,
                "lot_size": lot,
                "ai_status": "READY",
                "updated_at": datetime.now()
            }

            if not stock:
                db.add(StockDB(**data))
            else:
                for k, v in data.items():
                    setattr(stock, k, v)
            count += 1

        db.commit()
        print(f"[SUCCESS] Master stock population complete. Total: {count} stocks synced.")
    except Exception as e:
        print(f"[-] Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(populate())
