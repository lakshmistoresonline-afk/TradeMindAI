import asyncio
import os
import sys
import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine, text

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.core.container import container
from scripts.universe.nifty200_canonical import NIFTY_200_CONSTITUENTS

async def main():
    print("=== NIFTY-200 UNIVERSE & MODEL AUDIT ===")

    # 1. Connect to Neon
    DATABASE_URL = os.getenv("POSTGRES_URL")
    if not DATABASE_URL:
        print("POSTGRES_URL not found.")
        return

    engine = create_engine(DATABASE_URL)

    # 2. Map existing stocks and models
    with engine.connect() as conn:
        stocks_res = conn.execute(text("SELECT symbol, last_price, updated_at FROM stocks;"))
        stocks_map = {r[0]: r for r in stocks_res.fetchall()}

        models_res = conn.execute(text("SELECT symbol, version, accuracy, roc_auc, brier_score FROM model_registry WHERE is_champion=True;"))
        models_map = {r[0]: r for r in models_res.fetchall()}

        prices_count_res = conn.execute(text("SELECT symbol, count(*) FROM historical_prices GROUP BY symbol;"))
        prices_count_map = {r[0]: r[1] for r in prices_count_res.fetchall()}

        # Latest signal count
        signals_res = conn.execute(text("SELECT symbol, count(*) FROM live_signals GROUP BY symbol;"))
        signals_map = {r[0]: r[1] for r in signals_res.fetchall()}

    matrix = []

    for symbol in NIFTY_200_CONSTITUENTS:
        row = {
            "symbol": symbol,
            "membership_status": "MEMBER",
            "historical_bar_count": prices_count_map.get(symbol, 0),
            "model_status": "AVAILABLE" if symbol in models_map else "UNAVAILABLE",
            "model_id": models_map[symbol][1] if symbol in models_map else "N/A",
            "signal_count": signals_map.get(symbol, 0),
            "rejection_reason": "N/A"
        }

        if symbol not in stocks_map:
            row["membership_status"] = "UNIVERSE_MEMBER (NOT_IN_DB)"
            row["rejection_reason"] = "NOT_FOUND_IN_REGISTRY"
        elif row["historical_bar_count"] < 150:
            row["rejection_reason"] = "INSUFFICIENT_HISTORY"
            if row["model_status"] == "UNAVAILABLE":
                 row["model_status"] = "INSUFFICIENT_DATA"
        elif row["model_status"] == "UNAVAILABLE":
            row["rejection_reason"] = "MODEL_TRAINING_FAILED_OR_PENDING"

        matrix.append(row)

    df = pd.DataFrame(matrix)
    os.makedirs("reports", exist_ok=True)
    df.to_csv("reports/NIFTY200_FINAL_COVERAGE_MATRIX.csv", index=False)
    print(f"Exported coverage matrix: reports/NIFTY200_FINAL_COVERAGE_MATRIX.csv")

    # Summary
    print("\n--- SUMMARY ---")
    print(f"Total Monitored: {len(df)}")
    print(f"Models Available: {len(df[df.model_status == 'AVAILABLE'])}")
    print(f"Models Unavailable: {len(df[df.model_status != 'AVAILABLE'])}")
    print(f"Insufficient History (<150 bars): {len(df[df.rejection_reason == 'INSUFFICIENT_HISTORY'])}")
    print(f"Signals Generated (Total): {df.signal_count.sum()}")

if __name__ == "__main__":
    asyncio.run(main())
