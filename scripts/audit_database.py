import os
import sys
import datetime
from sqlalchemy import text
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load backend environment variables
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend", ".env"))

from backend.core.postgres import SessionLocal, StockDB

ALL_SUPPORTED = [
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

NIFTY_100 = ALL_SUPPORTED[:100]
EXTRA_SUPPORTED = ALL_SUPPORTED[100:]

def run_audit():
    session = SessionLocal()
    try:
        stocks = session.query(StockDB).all()
        db_symbols = {s.symbol for s in stocks}

        now = datetime.datetime.now(datetime.UTC)
        freshness_threshold = datetime.timedelta(hours=24)

        print(f"--- Final Data Fidelity Reconciliation Audit: {len(stocks)} Total Stocks ---")

        def get_fidelity(s):
            if not s: return False
            return bool(s.last_price and s.analysis and s.options_data and s.financial_history and s.health_metrics)

        def is_stale(s):
            if not s or not s.updated_at: return True
            ua = s.updated_at.replace(tzinfo=datetime.UTC)
            return (now - ua) > freshness_threshold

        nifty_db = [s for s in stocks if s.symbol in NIFTY_100]
        extra_db = [s for s in stocks if s.symbol in EXTRA_SUPPORTED]
        other_db = [s for s in stocks if s.symbol not in ALL_SUPPORTED]

        nifty_complete = [s for s in nifty_db if get_fidelity(s)]
        nifty_partial = [s for s in nifty_db if not get_fidelity(s)]
        nifty_missing = [s for s in NIFTY_100 if s not in db_symbols]
        nifty_stale = [s for s in nifty_db if is_stale(s)]

        extra_complete = [s for s in extra_db if get_fidelity(s)]
        extra_partial = [s for s in extra_db if not get_fidelity(s)]
        extra_stale = [s for s in extra_db if is_stale(s)]

        print(f"\n1. Nifty 100 Universe:")
        print(f"   - Complete (High-Fidelity): {len(nifty_complete)}")
        print(f"   - Partial:                {len(nifty_partial)}")
        print(f"   - Missing:                {len(nifty_missing)}")
        print(f"   - Stale (>24h):           {len(nifty_stale)}")

        print(f"\n2. Extra Supported Stocks (from Nifty Next 50/Midcap list):")
        print(f"   - Total in DB:            {len(extra_db)}")
        print(f"   - High-Fidelity:          {len(extra_complete)}")
        print(f"   - Partial:                {len(extra_partial)}")
        print(f"   - Stale:                  {len(extra_stale)}")

        if other_db:
            print(f"\n3. Other/Unknown Stocks in DB: {len(other_db)}")
            for o in other_db: print(f"   - {o.symbol}")

        total_fidelity = len([s for s in stocks if get_fidelity(s)])
        total_stale = len([s for s in stocks if is_stale(s)])

        coverage_pct = (len(stocks) / 100 * 100) # Against target universe
        fidelity_pct = (total_fidelity / 126 * 100) # Against total DB
        freshness_pct = ((len(stocks) - total_stale) / len(stocks) * 100) if stocks else 0

        print("\n--- Summary ---")
        print(f"Total: {len(stocks)} | High-Fidelity: {total_fidelity} | Stale: {total_stale} | Coverage: {coverage_pct:.1f}% | Fidelity: {fidelity_pct:.1f}% | Freshness: {freshness_pct:.1f}%")

        return {
            "total": len(stocks),
            "complete": total_fidelity,
            "stale": total_stale,
            "fidelity_pct": fidelity_pct,
            "freshness_pct": freshness_pct,
            "nifty": {
                "complete": len(nifty_complete),
                "partial": len(nifty_partial),
                "missing": len(nifty_missing)
            }
        }

    except Exception as e:
        print(f"Audit failed: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    run_audit()
