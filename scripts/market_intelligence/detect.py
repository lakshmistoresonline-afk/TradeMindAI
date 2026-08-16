import os
import sys
import asyncio
from datetime import datetime
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')

from backend.core.container import container
from backend.services.regime_engine import MarketRegimeEngine

async def run_detection():
    print("[*] Starting Market Regime Detection (Manual Local)...")
    try:
        provider = container.provider
        ios_repo = container.ios_repo

        # 1. Fetch Benchmarks
        nifty_df = await provider.fetch_history("^NSEI", period="6mo")
        vix_df = await provider.fetch_history("^INDIAVIX", period="6mo")

        if nifty_df.empty:
            print("[!] Error: Could not fetch Nifty data.")
            return

        # 2. Fetch Breadth (from Neon)
        stocks = await container.repository.get_all_stocks(limit=200)
        adv, dec = 0, 0
        for s in stocks:
            change = getattr(s, "change_pct", 0)
            if change and change > 0: adv += 1
            elif change and change < 0: dec += 1

        breadth = {"advancing": adv, "declining": dec}

        # 3. Detect
        regime = MarketRegimeEngine.detect_regime(nifty_df, vix_df, breadth)
        print(f"[+] Regime Detected: {regime.regime} (Sentiment: {regime.sentiment_score:.2f})")

        # 4. Persistence
        await ios_repo.save_market_regime(regime)
        print("[SUCCESS] Market Regime saved to Neon.")

    except Exception as e:
        print(f"[!] Error: {e}")

if __name__ == "__main__":
    asyncio.run(run_detection())
