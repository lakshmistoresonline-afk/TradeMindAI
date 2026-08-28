import asyncio
import os
import sys
from dotenv import load_dotenv
import pandas as pd

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')

from backend.core.container import container
from scripts.universe.nifty200_canonical import NIFTY_200_CONSTITUENTS
from backend.domain.models.ios import LiveSignal
from backend.services.price_resolver import PriceResolver

async def verify_coverage():
    print("--- TRADEMIND AI: NIFTY 200 EQUITY COVERAGE AUDIT ---")
    provider = container.provider

    results = []

    for symbol in NIFTY_200_CONSTITUENTS:
        print(f"[*] Verifying {symbol}...")

        status = "SUPPORTED"
        reason = "OK"

        try:
            # 1. Price Resolution Check
            dummy_sig = LiveSignal(
                id=f"cov_{symbol}",
                symbol=symbol,
                asset_class="EQUITY",
                direction="LONG",
                entry_price=100.0,
                timeframe="SWING",
                status="ACTIVE",
                rating="BUY",
                conviction=50.0
            )

            res = await PriceResolver.resolve_current_price(dummy_sig)

            if res["status"] == "DATA_UNAVAILABLE":
                status = "DATA_UNAVAILABLE"
                reason = "Provider returned no price"
            elif res["status"] == "INSTRUMENT_NOT_FOUND":
                status = "INVALID"
                reason = "Instrument ID mapping failed"
            elif res["status"] == "PROVIDER_UNSUPPORTED":
                status = "UNSUPPORTED"
                reason = "Provider does not support this symbol"

        except Exception as e:
            status = "ERROR"
            reason = str(e)

        results.append({
            "symbol": symbol,
            "equity_status": status,
            "reason": reason,
            "price": res.get("current_price") if status == "SUPPORTED" else None
        })

    df = pd.DataFrame(results)
    df.to_csv("docs/nifty200/NIFTY200_EQUITY_COVERAGE.csv", index=False)

    total = len(NIFTY_200_CONSTITUENTS)
    supported = len(df[df['equity_status'] == "SUPPORTED"])

    print(f"\n--- Coverage Results ---")
    print(f"Total Constituents: {total}")
    print(f"Supported:          {supported}")
    print(f"Coverage %:         {(supported/total)*100:.1f}%")

if __name__ == "__main__":
    asyncio.run(verify_coverage())
