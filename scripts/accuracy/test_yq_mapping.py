import os
import sys
import asyncio
import pandas as pd

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))

from backend.infrastructure.repositories.yfinance_provider import YFinanceProvider

async def test_mapping():
    provider = YFinanceProvider()
    symbols = ["GUJGASLTD", "LTIM", "PEL", "TATAMOTORS", "ZOMATO"]

    for s in symbols:
        mapped = provider._map_symbol(s)
        print(f"Symbol: {s} -> Mapped: {mapped}")
        df = await provider.fetch_history(s, period="1mo")
        print(f"   History rows: {len(df)}")
        if not df.empty:
            print(f"   Last date: {df.index[-1]}")
        else:
            print(f"   [!] History EMPTY")

if __name__ == "__main__":
    asyncio.run(test_mapping())
