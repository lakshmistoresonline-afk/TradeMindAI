import asyncio
import datetime
import sys
import os

# Set up paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", "backend", ".env"))

from backend.core.container import container
from backend.services.universe_service import UniverseService

async def train_all():
    print("=== [PHASE 8-11] Training Multi-Horizon Models (FULL UNIVERSE) ===")

    symbols = UniverseService.NIFTY_200_CONSTITUENTS[:50]
    horizons = ["SHORT", "SWING", "LONG"]

    ml_service = container.ml_service
    repo = container.data_platform_repo

    start_date = datetime.datetime.utcnow() - datetime.timedelta(days=1000)
    end_date = datetime.datetime.utcnow()

    for symbol in symbols:
        print(f"   [SYMBOL] {symbol}")
        for horizon in horizons:
            try:
                # 1. Fetch features for specific horizon
                features = await repo.get_features_by_range(symbol, start_date, end_date, horizon=horizon)
                if not features:
                    print(f"      [!] {horizon}: No features found.")
                    continue

                # 2. Train and Register
                metadata = await ml_service.train_and_register(symbol, features, horizon=horizon)
                print(f"      [OK] {horizon}: AUC={metadata.roc_auc:.4f}, Brier={metadata.brier_score:.4f}")

            except Exception as e:
                print(f"      [ERROR] {horizon} failed: {e}")

if __name__ == "__main__":
    asyncio.run(train_all())
