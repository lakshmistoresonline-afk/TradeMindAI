import os
import sys
import asyncio
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')

from backend.core.container import container
from backend.domain.models.data_platform import FeatureVector

async def generate_targets(symbol: str, horizon: int = 50):
    """
    Forensic Target Generation:
    TARGET = 1 if Price hits +3% before -1.5% within Horizon bars.
    """
    print(f"[*] Generating labels for {symbol}...")

    # 1. Fetch ALL historical candles
    df = await container.provider.fetch_history(symbol, period="2y", interval="1d")
    if df.empty: return

    # 2. Iterate through each bar T
    labels = []
    for i in range(len(df) - horizon):
        entry_price = df.iloc[i]["Close"]
        future_window = df.iloc[i+1 : i+1+horizon]

        target_hit = False
        stop_hit = False

        # Binary target: 3% profit vs 1.5% loss
        target_price = entry_price * 1.03
        stop_price = entry_price * 0.985

        for _, row in future_window.iterrows():
            if row["High"] >= target_price:
                target_hit = True
                break
            if row["Low"] <= stop_price:
                stop_hit = True
                break

        # Label 1 for Win, 0 for Loss/Timeout
        labels.append(1 if target_hit else 0)

    # 3. Update Feature Store with real labels
    # This assumes features already exist for these timestamps
    print(f"   [+] Generated {len(labels)} real outcome labels.")

    # In a full system, we would batch update the Postgres 'target' column in feature_vectors
    # For now, we print verification.

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--symbol", default="NIFTY")
    args = parser.parse_args()
    asyncio.run(generate_targets(args.symbol))
