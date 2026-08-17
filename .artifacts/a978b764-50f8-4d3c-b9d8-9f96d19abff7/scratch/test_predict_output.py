import asyncio
import os
import sys
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')

from backend.core.container import container

async def test():
    symbol = 'RELIANCE'
    # Mock features that match what was trained
    feats = {
        'trend_ema_cross': 1.0,
        'momentum_rsi': 0.6,
        'volatility_bb': 0.5,
        'volume_relative': 1.2,
        'smc_bullish_ob': 0.0,
        'smc_bearish_ob': 0.0,
        'ict_liquidity_void': 0.0
    }
    res = await container.ml_service.predict_with_champion(symbol, feats)
    print("--- Predict Output ---")
    print(res)
    print(f"Has metadata: {'metadata' in res}")

if __name__ == "__main__":
    asyncio.run(test())
