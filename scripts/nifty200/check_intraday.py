import os
import sys
import asyncio
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')

from backend.core.container import container

async def main():
    print("[*] Checking Intraday (1m) Availability...")
    provider = container.provider
    symbols = ["RELIANCE", "NIFTY", "BANKNIFTY", "INFY"]

    for s in symbols:
        try:
            df = await provider.fetch_history(s, period="1d", interval="1m")
            print(f"   - {s:<12} | 1m Candles: {len(df)}")
        except Exception as e:
            print(f"   - {s:<12} | ERROR: {e}")

if __name__ == "__main__":
    asyncio.run(main())
