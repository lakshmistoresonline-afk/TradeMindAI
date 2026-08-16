import os
import sys
import asyncio
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')

from backend.core.container import container

async def test():
    symbol = "ZOMATO"
    print(f"[*] Testing full collect_stock_data for {symbol}")
    try:
        # 1. Try history via provider
        df = await container.provider.fetch_history(symbol, "1mo")
        print(f"Provider history empty: {df.empty}")
        if not df.empty:
            print(df.head())

        # 2. Try raw yahooquery for MSFT to confirm environment
        from yahooquery import Ticker
        print(f"MSFT test: {not Ticker('MSFT').history(period='5d').empty}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test())
