import asyncio
import os
import sys
from dotenv import load_dotenv
import pandas as pd
import yfinance as yf

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')

from backend.core.container import container
from scripts.universe.nifty200_canonical import NIFTY_200_CONSTITUENTS

async def audit_fo():
    print("--- TRADEMIND AI: NIFTY 200 F&O ELIGIBILITY AUDIT ---")
    provider = container.provider

    results = []

    for symbol in NIFTY_200_CONSTITUENTS:
        print(f"[*] Auditing {symbol}...")

        # Check if futures/options exist via yfinance as a proxy if provider is limited
        # or use provider if it has a way to check.
        # Yahoo Finance check: if symbol.options is not empty
        ticker = yf.Ticker(f"{symbol}.NS")

        try:
            options = ticker.options
            has_options = len(options) > 0
        except:
            has_options = False

        # Groww Provider usually has a way to check if instrument is F&O
        # For now, let's use a heuristic or pre-defined list if available.
        # Professional implementation would fetch from NSE Master Copy.

        # Let's assume if it has options on Yahoo, it's F&O eligible for our purposes.
        is_fo = has_options

        results.append({
            "symbol": symbol,
            "fo_eligible": is_fo,
            "options_count": len(options) if is_fo else 0
        })

    df = pd.DataFrame(results)
    df.to_csv("docs/nifty200/NIFTY200_FO_ELIGIBILITY.csv", index=False)
    print(f"\n[SUCCESS] F&O Audit Complete. Found {df['fo_eligible'].sum()} eligible stocks.")

if __name__ == "__main__":
    asyncio.run(audit_fo())
