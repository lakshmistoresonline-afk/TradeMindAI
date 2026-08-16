import os
import sys
import asyncio
from datetime import datetime
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')

from backend.core.container import container
from scripts.universe.nifty200_canonical import NIFTY_200_CONSTITUENTS

async def train():
    print(f"[*] Starting Champion Training for {len(NIFTY_200_CONSTITUENTS)} stocks...")

    ml_service = container.ml_service

    for symbol in NIFTY_200_CONSTITUENTS:
        print(f"   [*] Processing {symbol}...")
        try:
            # 1. Fetch features (If they exist)
            features = await container.data_platform_repo.get_features_by_range(
                symbol,
                datetime(2020, 1, 1),
                datetime.utcnow()
            )

            if not features or len(features) < 100:
                print(f"      [SKIP] Insufficient features for {symbol} ({len(features) if features else 0})")
                continue

            # 2. Train
            print(f"      [TRAIN] Training model for {symbol}...")
            metadata = await ml_service.train_and_register(symbol, features)
            print(f"      [SUCCESS] Registered model version: {metadata.version}")

        except Exception as e:
            print(f"      [ERROR] {symbol}: {e}")

if __name__ == "__main__":
    asyncio.run(train())
