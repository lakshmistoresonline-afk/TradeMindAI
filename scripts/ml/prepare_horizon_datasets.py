import asyncio
import pandas as pd
import numpy as np
import datetime
import sys
import os

# Set up paths for importing backend modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.core.container import container
from backend.analysis.technical import TechnicalAnalysis
from backend.services.feature_store import FeatureStoreService
from backend.services.horizon_label_service import HorizonLabelService
from backend.services.universe_service import UniverseService
from backend.core.duckdb_engine import analytical_engine

async def prepare_datasets():
    print("=== [PHASE 5] Preparing Canonical Horizon Datasets ===")

    symbols = UniverseService.NIFTY_200_CONSTITUENTS
    horizons = ["SHORT", "SWING", "LONG"]

    feature_store = FeatureStoreService(container.data_platform_repo)

    # Ensure universe is synced
    await UniverseService(container.repository, container.provider).sync_universe()

    for symbol in symbols:
        print(f"   [PROCESS] {symbol}...")
        try:
            # 1. Fetch history (limit to 1000 days for depth)
            prices = await container.repository.get_recent_prices(symbol, limit=1000)
            if not prices:
                print(f"      [!] No price data for {symbol}")
                continue

            df = pd.DataFrame([p.model_dump() for p in prices])
            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)
            df.sort_index(inplace=True)

            if len(df) < 200:
                print(f"      [!] Insufficient history for {symbol}: {len(df)} bars")
                continue

            # 2. Calculate Technical Indicators
            df_ta = TechnicalAnalysis.calculate_indicators(df)

            # 3. Extract Features and Labels for each horizon
            all_features = []
            for ts, row in df_ta.iterrows():
                feat = feature_store.extract_institutional_features(df_ta, smc_data={}, timestamp=ts)
                if feat:
                    feat['date'] = ts
                    all_features.append(feat)

            if not all_features:
                continue

            feat_df = pd.DataFrame(all_features)
            feat_df.set_index('date', inplace=True)

            # 4. Calculate Labels
            # The features already contain Close, High, Low now.
            for horizon in horizons:
                HorizonLabelService.apply_labels_to_dataset(feat_df, horizon=horizon)

            # 5. Ingest into DuckDB
            final_df = feat_df.reset_index()
            analytical_engine.ingest_features(symbol, final_df)
            print(f"      [OK] {symbol} dataset ready. Size: {len(final_df)}")

        except Exception as e:
            print(f"      [ERROR] {symbol} failed: {e}")

if __name__ == "__main__":
    asyncio.run(prepare_datasets())
