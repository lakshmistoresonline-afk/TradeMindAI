import os
import sys
import asyncio
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')
os.environ["TRADEMIND_EXECUTION_MODE"] = "local"

from backend.core.container import container

async def test_ranges():
    symbol = "RELIANCE"
    dp_repo = container.data_platform_repo

    print("\n--- FEATURE STORE RANGE TEST ---")

    # Test 1: Recent Range (7 days)
    end = datetime.utcnow()
    start = end - timedelta(days=7)
    feats = await dp_repo.get_features_by_range(symbol, start, end)
    print(f"Testing {symbol} 7-day range: {len(feats)} vectors")
    assert len(feats) > 0, "No features found in recent 7-day range"

    # Test 2: Historical Range (2022)
    start_hist = datetime(2022, 1, 1)
    end_hist = datetime(2022, 12, 31)
    feats_hist = await dp_repo.get_features_by_range(symbol, start_hist, end_hist)
    print(f"Testing {symbol} 2022 range: {len(feats_hist)} vectors")
    assert len(feats_hist) > 200, f"Expected ~250 vectors for 2022, found {len(feats_hist)}"

    print("[PASS] Feature Store range queries verified.")

if __name__ == "__main__":
    asyncio.run(test_ranges())
