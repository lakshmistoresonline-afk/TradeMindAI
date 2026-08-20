
import os
import sys
import asyncio
import pandas as pd
import numpy as np
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

    df['SMA_20'] = df['Close'].rolling(window=20).mean()
    high_low = df['High'] - df['Low']
    high_cp = np.abs(df['High'] - df['Close'].shift())
    low_cp = np.abs(df['Low'] - df['Close'].shift())
    df['TR'] = np.maximum(high_low, np.maximum(high_cp, low_cp))
    df['ATR'] = df['TR'].rolling(window=14).mean()

    df['magnitude'] = (df['Close'] - df['SMA_20']).abs()
    df['gate'] = df['ATR'] * 0.5

    print(df[['Close', 'SMA_20', 'magnitude', 'ATR', 'gate']].tail(20))

    passes = len(df[df['magnitude'] >= df['gate']])
    print(f"\nBars passing magnitude gate: {passes} / {len(df)}")

if __name__ == "__main__":
    asyncio.run(debug())
