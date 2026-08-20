import os
import sys
import asyncio
import pandas as pd
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')
os.environ["TRADEMIND_EXECUTION_MODE"] = "local"

from backend.core.container import container

async def main():
    symbol = 'ADANIENT'
    signal_date = pd.to_datetime('2023-02-28')
    entry_price = 1361.37

    prices = await container.repository.get_recent_prices(symbol, limit=5000)
    df = pd.DataFrame([p.model_dump() for p in prices])
    df.set_index('date', inplace=True)
    df.sort_index(inplace=True)
    df.columns = [c.capitalize() for c in df.columns]

    idx = df.index.get_indexer([signal_date], method='nearest')[0]
    print(f"Signal Date: {df.index[idx]} | Entry Price: {entry_price}")

    next_bars = df.iloc[idx+1:idx+5]
    print("Next bars:")
    print(next_bars[['Open', 'High', 'Low', 'Close']])

    for i, row in next_bars.iterrows():
        low, high = row['Low'], row['High']
        triggered = (low <= entry_price <= high)
        print(f"Date: {i} | Low: {low} | High: {high} | Triggered: {triggered}")

if __name__ == "__main__":
    asyncio.run(main())
