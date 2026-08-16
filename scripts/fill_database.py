import os
import sys
import asyncio
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load backend environment variables
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend", ".env"))

from backend.workers.tasks import _analyze_stock_logic
from backend.core.postgres import SessionLocal, StockDB

NIFTY_100 = [
    "ABB", "ACC", "ADANIENSOL", "ADANIENT", "ADANIGREEN", "ADANIPORTS", "ADANIPOWER", "ATGL", "AMBUJACEM", "APOLLOHOSP",
    "ASHOKLEY", "ASIANPAINT", "ASTRAL", "AXISBANK", "BAJAJ-AUTO", "BAJFINANCE", "BAJAJFINSV", "BAJAJHLDNG", "BALKRISIND",
    "BANDHANBNK", "BANKBARODA", "BANKINDIA", "BEL", "BHEL", "BPCL", "BHARTIARTL", "BIOCON", "BOSCHLTD", "BRITANNIA",
    "CANBK", "CGPOWER", "CHOLAFIN", "CIPLA", "COALINDIA", "COLPAL", "CONCOR", "CUMMINSIND", "DLF", "DABUR",
    "DALBHARAT", "DEEPAKNTR", "DRREDDY", "EICHERMOT", "ESCORTS", "GAIL", "GMRINFRA", "GLAND", "GODREJCP", "GODREJPROP",
    "GRASIM", "GUJGASLTD", "HAL", "HCLTECH", "HDFCBANK", "HDFCLIFE", "HAVELLS", "HEROMOTOCO", "HINDALCO", "HINDUNILVR",
    "ICICIBANK", "ICICIGI", "ICICIPRULI", "IDFCFIRSTB", "ITC", "INDHOTEL", "INDIANB", "INDUSINDBK", "INDUSTOWER", "INFY",
    "INTERGLOBE", "IOC", "IRCTC", "IRFC", "JSWENERGY", "JSWSTEEL", "JINDALSTEL", "JUBLFOOD", "KOTAKBANK", "LTIM",
    "LT", "LICHSGFIN", "LICI", "MRF", "M&M", "MARICO", "MARUTI", "MAXHEALTH", "MAHABANK", "MPHASIS",
    "NHPC", "NMDC", "NTPC", "NESTLEIND", "NYKAA", "ONGC", "PAYTM", "PIIND", "PNB", "PFC",
    "PAGEIND", "PATANJALI", "PIDILITIND", "POLYCAB", "POWERGRID", "PRESTIGE", "RVNL", "RECLTD", "RELIANCE", "SBICARD",
    "SBILIFE", "SBIN", "SRF", "SHREECEM", "SHRIRAMFIN", "SIEMENS", "SONACOMS", "SUNPHARMA", "SUNTV",
    "SUPREMEIND", "SYNGENE", "TATACOMM", "TATACONSUM", "TATAMOTORS", "TATAMTRDVR", "TATAPOWER", "TATASTEEL", "TCS", "TECHM",
    "TITAN", "TORNTPHARM", "TRENT", "TIINDIA", "UPL", "ULTRACEMCO", "UNITDSPR", "VBL", "VEDL", "WIPRO",
    "YESBANK", "ZOMATO", "ZYDUSLIFE"
]

async def fill():
    # Limit to top 5 for verification to save time/API
    targets = NIFTY_100[:5]
    print(f"Triggering analysis for {len(targets)} stocks: {targets}")

    for symbol in targets:
        try:
            print(f"Analyzing {symbol}...")
            # Using period="1mo" for faster fill
            await _analyze_stock_logic(symbol, period="1mo")
        except Exception as e:
            print(f"Failed {symbol}: {e}")

if __name__ == "__main__":
    asyncio.run(fill())
