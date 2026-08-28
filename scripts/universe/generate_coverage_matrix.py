import asyncio
import os
import sys
from dotenv import load_dotenv
import pandas as pd
from sqlalchemy import text

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')

from backend.core.container import container
from backend.core.postgres import SessionLocal, StockDB
from scripts.universe.nifty200_canonical import NIFTY_200_CONSTITUENTS
from backend.domain.models.ios import LiveSignal
from backend.services.price_resolver import PriceResolver

async def generate_matrix():
    print("--- TRADEMIND AI: NIFTY 200 MASTER COVERAGE MATRIX ---")
    provider = container.provider

    # Authoritative F&O map from DB
    session = SessionLocal()
    try:
        stocks_db = session.query(StockDB).all()
        fno_map = {s.symbol: s.is_fno for s in stocks_db}
        print(f"[*] Loaded {len(fno_map)} symbols from DB for F&O mapping.")
    finally:
        session.close()

    matrix = []

    for symbol in NIFTY_200_CONSTITUENTS:
        print(f"[*] Auditing {symbol}...")

        row = {
            "symbol": symbol,
            "universe_version": "NIFTY_200_AUG2026",
            "provider": provider.__class__.__name__
        }

        # 1. Equity Status
        status = "SUPPORTED"
        res = {"status": "UNKNOWN"}
        try:
            dummy_sig = LiveSignal(
                id=f"audit_{symbol}", symbol=symbol, asset_class="EQUITY",
                direction="LONG", entry_price=100.0, timeframe="SWING",
                status="ACTIVE", rating="BUY", conviction=50.0
            )
            res = await PriceResolver.resolve_current_price(dummy_sig)
            row["equity_instrument_id"] = f"{symbol}.NS"
            row["equity_data_status"] = res["status"]
            row["signal_capable"] = (res["status"] == "FRESH")
        except Exception as e:
            row["equity_data_status"] = "ERROR"
            row["signal_capable"] = False
            print(f"   [!] Error resolving {symbol}: {e}")

        # 2. F&O Status
        is_fno = fno_map.get(symbol, False)
        row["futures_eligible"] = is_fno
        row["options_eligible"] = is_fno

        matrix.append(row)

    df = pd.DataFrame(matrix)
    df.to_csv("docs/nifty200/NIFTY200_COMPLETE_COVERAGE_MATRIX.csv", index=False)
    print(f"\n[SUCCESS] Matrix Generated: docs/nifty200/NIFTY200_COMPLETE_COVERAGE_MATRIX.csv")

if __name__ == "__main__":
    asyncio.run(generate_matrix())
