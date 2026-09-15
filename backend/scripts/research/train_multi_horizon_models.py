import asyncio
import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.core.container import container
from backend.services.research_feature_engine import ResearchFeatureEngine
from backend.domain.models.data_platform import FeatureVector

async def train_for_symbol(symbol: str):
    print(f"--- Training Multi-Horizon Models for {symbol} ---")

    horizons = ["SHORT", "SWING", "LONG"]

    for h in horizons:
        try:
            print(f"   [{h}] Building dataset...")
            dataset = await ResearchFeatureEngine.build_horizon_dataset(symbol, h)

            if dataset.empty or len(dataset) < 150:
                print(f"   [{h}] Skipped: Insufficient data ({len(dataset)} rows)")
                continue

            # Convert DF rows to FeatureVector objects for MLService
            features = []
            for ts, row in dataset.iterrows():
                features.append(FeatureVector(
                    symbol=symbol,
                    date=ts,
                    version="v1.0.0",
                    features={k: float(v) for k, v in row.items() if k != "target"},
                    target=float(row["target"])
                ))

            print(f"   [{h}] Training model...")
            metadata = await container.ml_service.train_and_register(symbol, features, horizon=h)

            # Set as champion
            metadata.is_champion = True
            metadata.status = "CHAMPION"
            await container.data_platform_repo.save_model_metadata(metadata)

            print(f"   [{h}] SUCCESS: Accuracy={metadata.accuracy:.2f}, AUC={metadata.roc_auc:.2f}")

        except Exception as e:
            print(f"   [{h}] ERROR: {str(e)}")

async def main():
    symbols = container.universe_service.NIFTY_200_CONSTITUENTS

    # Process in chunks to manage concurrency
    chunk_size = 5
    for i in range(0, len(symbols), chunk_size):
        chunk = symbols[i:i+chunk_size]
        tasks = [train_for_symbol(s) for s in chunk]
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
