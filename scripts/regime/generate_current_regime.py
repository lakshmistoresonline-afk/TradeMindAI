import asyncio
import datetime
import sys
import os
import pandas as pd

# Set up paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", "backend", ".env"))

from backend.core.container import container
from backend.services.regime_engine import MarketRegimeEngine

async def generate_regime():
    print("=== Generating Current Market Regime ===")

    provider = container.provider
    repo = container.ios_repo

    # 1. Fetch NIFTY index data
    nifty_df = await provider.get_history("^NSEI", start_date=datetime.datetime.utcnow() - datetime.timedelta(days=365))

    # 2. Fetch VIX data
    vix_df = await provider.get_history("INDIAVIX.NS", start_date=datetime.datetime.utcnow() - datetime.timedelta(days=30))

    # 3. Detect Regime
    regime = MarketRegimeEngine.detect_regime(nifty_df, vix_df)

    # 4. Save to Repository
    await repo.save_market_regime(regime)

    print(f"Regime Generated: {regime.regime} (Sentiment: {regime.sentiment_score:.2f})")
    print(f"Description: {regime.description}")

if __name__ == "__main__":
    asyncio.run(generate_regime())
