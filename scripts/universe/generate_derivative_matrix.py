import asyncio
import os
import sys
from dotenv import load_dotenv
import pandas as pd
from sqlalchemy import text

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')

from backend.core.postgres import SessionLocal, StockDB

async def generate_derivative_matrix():
    print("--- TRADEMIND AI: DERIVATIVE COVERAGE MATRIX ---")
    session = SessionLocal()

    try:
        # Authoritative F&O map from DB
        fno_stocks = session.query(StockDB).filter(StockDB.is_fno == True).all()
        print(f"[*] Found {len(fno_stocks)} F&O eligible stocks.")

        matrix = []

        # Add NIFTY/BANKNIFTY indices
        indices = ["NIFTY", "BANKNIFTY"]

        for u in indices + [s.symbol for s in fno_stocks]:
            # Add Near Month Futures (Synthetic placeholder for coverage report)
            # Since discovery is limited, we show eligibility status
            matrix.append({
                "underlying": u,
                "instrument_type": "FUTURE",
                "instrument_id": f"{u}_NEAR_FUT",
                "price": None,
                "price_status": "PROVIDER_UNSUPPORTED",
                "eligibility": "F&O_ELIGIBLE"
            })

            matrix.append({
                "underlying": u,
                "instrument_type": "OPTION",
                "instrument_id": f"{u}_ATM_CE",
                "price": None,
                "price_status": "PROVIDER_UNSUPPORTED",
                "eligibility": "F&O_ELIGIBLE"
            })

        df = pd.DataFrame(matrix)
        df.to_csv("docs/nifty200/NIFTY200_DERIVATIVE_COVERAGE_MATRIX.csv", index=False)
        print(f"\n[SUCCESS] Derivative Matrix Generated: {len(df)} contract-rows.")

    finally:
        session.close()

if __name__ == "__main__":
    asyncio.run(generate_derivative_matrix())
