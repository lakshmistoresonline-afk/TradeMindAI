import asyncio
import os
import sys
import datetime
from dotenv import load_dotenv
from sqlalchemy import text

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Load environment
load_dotenv(os.path.join(os.path.dirname(__file__), '../backend/.env'))

from backend.core.container import container
from backend.workers.tasks import _analyze_stock_logic
from backend.core.postgres import init_db, engine

async def verify_and_populate():
    print("\n" + "="*60)
    print("TRADE MIND AI: ONE-BY-ONE NIFTY 100 VERIFICATION & POPULATION")
    print("="*60 + "\n")

    # 1. Initialize shared database
    init_db()

    symbols = [
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

    # Process in batches of 5 to prevent session timeouts
    batch_size = 5
    processed = 0

    for i, symbol in enumerate(symbols):
        if processed >= batch_size:
            print(f"\n✅ Finished mini-batch of {batch_size}. Stopping for now.")
            break

        try:
            print(f"[{i+1}/{len(symbols)}] Verifying {symbol}...")

            # Check current status in DB
            with engine.connect() as conn:
                res = conn.execute(text("SELECT analysis, updated_at, structured_consensus FROM stocks WHERE symbol = :s"), {"s": symbol}).fetchone()

            needs_update = False
            if not res:
                print(f"  🆕 {symbol}: Missing from database. Initializing...")
                needs_update = True
            else:
                analysis, updated_at, structured = res
                if not analysis or not structured:
                    print(f"  ⚠️ {symbol}: Incomplete DNA found. Repairing...")
                    needs_update = True
                elif updated_at.date() < datetime.date.today():
                    print(f"  ⏳ {symbol}: Outdated research (from {updated_at.date()}). Updating...")
                    needs_update = True
                else:
                    print(f"  ✅ {symbol}: Data is up-to-date. Skipping.")

            if needs_update:
                processed += 1
                # Trigger analysis logic
                result = await _analyze_stock_logic(symbol, period="10y")

                if "Error" in str(result):
                    print(f"  ❌ {symbol}: Analysis failed - {str(result)[:100]}")
                else:
                    print(f"  ✨ {symbol}: Research DNA successfully populated.")

                # Groq Token Guard: Wait between individual stock analyses
                print(f"  (Rate limit cooldown: 30s)")
                await asyncio.sleep(30)

        except Exception as e:
            print(f"  💥 {symbol}: Error during verification - {e}")

    print("\n" + "="*60)
    print("PROCESS COMPLETE")
    print("="*60 + "\n")

if __name__ == "__main__":
    asyncio.run(verify_and_populate())
