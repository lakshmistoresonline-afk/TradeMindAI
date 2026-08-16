import os
import sys
import asyncio
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')

from backend.core.container import container

async def debug():
    symbol = "RELIANCE"
    features = await container.data_platform_repo.get_features_by_range(
        symbol, datetime(2020, 1, 1), datetime.utcnow()
    )
    print(f"Total features fetched: {len(features)}")
    if features:
        print(f"Sample features: {features[0].features.keys()}")
        print(f"Sample target: {features[0].target}")

        try:
            metadata = await container.ml_service.train_and_register(symbol, features)
            print("Training Success!")
        except Exception as e:
            print(f"Training Failed: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug())
