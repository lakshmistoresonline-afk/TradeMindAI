import os
import sys
import datetime
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load backend environment variables
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend", ".env"))

from backend.core.postgres import StockDB, DATABASE_URL

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

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

def check():
    session = Session()
    stocks = session.query(StockDB).all()

    print(f"Total in DB: {len(stocks)}")

    incomplete = []
    for symbol in NIFTY_100:
        stock = next((s for s in stocks if s.symbol == symbol), None)
        if not stock:
            incomplete.append((symbol, "MISSING"))
        else:
            is_complete = stock.last_price and stock.analysis and stock.options_data and stock.financial_history and stock.health_metrics
            if not is_complete:
                incomplete.append((symbol, "PARTIAL"))

    print(f"Incomplete (Nifty 100): {len(incomplete)}")
    for s, reason in incomplete[:10]:
        print(f"  {s}: {reason}")

    session.close()

if __name__ == "__main__":
    check()
