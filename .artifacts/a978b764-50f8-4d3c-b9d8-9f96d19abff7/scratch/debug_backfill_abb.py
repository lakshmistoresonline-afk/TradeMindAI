import os
import sys
import asyncio
import pandas as pd
import numpy as np
from datetime import datetime
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')

from backend.core.container import container

async def debug():
    symbol = "ABB"
    repo = container.repository
    prices = await repo.get_recent_prices(symbol, limit=5000)
    df = pd.DataFrame([p.model_dump() for p in prices])
    df.set_index('date', inplace=True)
    df.columns = [c.capitalize() for c in df.columns]

    print(f"Initial df shape: {df.shape}")

    df['target_return'] = df['Close'].shift(-5) / df['Close'] - 1
    df['target'] = (df['target_return'] > 0.01).astype(float)

    print(f"Target distribution before dropna:\n{df['target'].value_counts(dropna=False)}")
    print(f"Target NaNs: {df['target'].isna().sum()}")

    feat_df = pd.DataFrame(index=df.index)
    feat_df['target'] = df['target']
    feat_df.dropna(inplace=True)
    print(f"Feat df shape after dropna: {feat_df.shape}")

if __name__ == "__main__":
    asyncio.run(debug())
