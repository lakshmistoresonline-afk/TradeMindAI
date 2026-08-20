
import os
import sys
import asyncio
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')
os.environ["TRADEMIND_EXECUTION_MODE"] = "local"

from backend.core.container import container

async def debug():
    symbol = "RELIANCE"
    print(f"--- DEBUG REPO: {symbol} ---")
    try:
        prices = await container.repository.get_recent_prices(symbol, limit=10)
        print(f"Success: {len(prices)} prices found.")
        for p in prices:
            print(p)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug())
