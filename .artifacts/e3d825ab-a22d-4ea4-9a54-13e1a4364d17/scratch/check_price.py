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
    symbol = 'ADANIPOWER'
    prices = await container.repository.get_recent_prices(symbol, limit=5000)
    df = pd.DataFrame([p.model_dump() for p in prices])
    df.set_index('date', inplace=True)
    df.sort_index(inplace=True)

    print(f"ADANIPOWER prices near 2021-08-24:")
    target_date = '2021-08-24'
    idx = df.index.get_indexer([pd.to_datetime(target_date)], method='nearest')[0]
    print(df.iloc[idx-5:idx+205])

if __name__ == "__main__":
    asyncio.run(main())
