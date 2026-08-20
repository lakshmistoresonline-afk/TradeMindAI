
import os
import sys
import asyncio
import pandas as pd
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')
os.environ["TRADEMIND_EXECUTION_MODE"] = "local"

from backend.core.container import container

async def debug():
    symbol = "SBIN"
    prices = await container.repository.get_recent_prices(symbol, limit=1000)
    df = pd.DataFrame([p.model_dump() for p in prices])
    df.columns = [c.capitalize() for c in df.columns]

    print(f"SBIN rows: {len(df)}")
    count_10m = len(df[df['Volume'] > 10000000])
    print(f"Rows with >10M Volume: {count_10m}")

    # Check EMA 200
    df['EMA_200'] = df['Close'].ewm(span=200, adjust=False).mean()
    print(f"EMA 200 (bar 200): {df['EMA_200'].iloc[200]}")
    print(f"Close (bar 200): {df['Close'].iloc[200]}")

if __name__ == "__main__":
    asyncio.run(debug())
