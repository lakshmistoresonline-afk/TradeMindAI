import asyncio
import os
import sys
import datetime
from dotenv import load_dotenv

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Load environment
load_dotenv(os.path.join(os.path.dirname(__file__), '../backend/.env'))

from backend.core.container import container
from backend.workers.tasks import _analyze_stock_logic, _process_intel_logic
from backend.core.postgres import init_db

async def populate():
    print("\n" + "="*60)
    print("TRADE MIND AI: FULL NIFTY 100 PRODUCTION POPULATION")
    print("="*60 + "\n")

    # 1. Initialize shared database (PostgreSQL/Neon)
    init_db()
    print("✅ Database schema verified.")

    # 2. Define the Nifty 100 Ticker List
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

    print(f"Starting ingestion for {len(symbols)} stocks with 10Y history and 12-Agent Analysis...")
    print("Estimated time: ~45 minutes (to stay within AI rate limits)\n")

    success_count = 0
    failed_count = 0

    for i, symbol in enumerate(symbols):
        try:
            print(f"[{i+1}/{len(symbols)}] Processing {symbol}...")

            # RC-4 Optimization: Skip if already analyzed with consensus today
            existing = await container.repository.get_stock_by_symbol(symbol)
            if existing and existing.analysis and existing.updated_at.date() == datetime.date.today():
                print(f"  ⏭️  {symbol}: Already up-to-date. Skipping.")
                success_count += 1
                continue

            result = await _analyze_stock_logic(symbol, period="10y")

            if "Error" in str(result):
                print(f"  ⚠️  {symbol}: Partial Success / Warning: {str(result)[:100]}...")
            else:
                print(f"  ✅ {symbol}: COMPLETED")

            success_count += 1

            # RC-4 Guardrail: Wait 30 seconds between stocks to clear Groq Token Quota (TPM)
            if i < len(symbols) - 1:
                await asyncio.sleep(30)

        except Exception as e:
            print(f"  ❌ {symbol}: CRITICAL FAILURE - {e}")
            failed_count += 1

    # 3. Generate Global Market Intelligence
    print("\n--- FINAL STEP: GENERATING MARKET INTELLIGENCE REPORT ---")
    try:
        await _process_intel_logic()
        print("✅ Global market regime and institutional bias updated.")
    except Exception as e:
        print(f"❌ Intelligence generation failed: {e}")

    print("\n" + "="*60)
    print(f"POPULATION SUMMARY")
    print(f"Total Attempted: {len(symbols)}")
    print(f"Success/Partial: {success_count}")
    print(f"Failed         : {failed_count}")
    print("="*60 + "\n")

if __name__ == "__main__":
    asyncio.run(populate())
