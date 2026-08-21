import os
import sys
import asyncio
from datetime import datetime
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')
os.environ["TRADEMIND_EXECUTION_MODE"] = "local"

from backend.core.container import container

async def train():
    symbols = ["PEL", "TATAMOTORS", "ZOMATO", "GMRINFRA", "L&TFH"]
    ml_service = container.ml_service
    dp_repo = container.data_platform_repo

    print("--- TRAINING MODELS FOR PROBLEM SYMBOLS ---")

    for s in symbols:
        print(f"[*] Training {s}...")
        try:
            feats = await dp_repo.get_features_by_range(s, datetime(2010, 1, 1), datetime(2026, 8, 21))
            print(f"   [+] Features count: {len(feats)}")

            if len(feats) < 150:
                print(f"   [!] Insufficient features for calibrated training ({len(feats)})")
                continue

            metadata = await ml_service.train_and_register(s, feats)
            print(f"   [SUCCESS] Champion Model: {metadata.name} (Acc: {metadata.accuracy:.2f})")
        except Exception as e:
            print(f"   [ERROR] {s}: {e}")

if __name__ == "__main__":
    asyncio.run(train())
