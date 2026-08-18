
import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')

from backend.core.container import container
from backend.services.outcome_engine import OutcomeEngine
from backend.domain.models.ios import LiveSignal

async def run_baselines():
    print("--- SIMPLE BASELINE COMPARISON ---")

    symbols = ["RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK"]

    # Test Period: Last 12 months
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)

    results = []

    for symbol in symbols:
        prices = await container.repository.get_recent_prices(symbol, limit=2000)
        df = pd.DataFrame([p.model_dump() for p in prices])
        df.set_index('date', inplace=True)
        df.sort_index(inplace=True)
        df.columns = [c.capitalize() for c in df.columns]

        test_df = df[df.index >= pd.Timestamp(start_date)]
        if test_df.empty: continue

        # 1. Buy & Hold
        bh_ret = (test_df['Close'].iloc[-1] / test_df['Close'].iloc[0] - 1) * 100

        # 2. EMA Trend Strategy (Simple)
        df['ema_200'] = df['Close'].rolling(200).mean()
        ema_trades = []
        for i in range(200, len(df)-20, 5):
            date = df.index[i]
            if date < pd.Timestamp(start_date): continue

            price = df.iloc[i]['Close']
            ema = df.iloc[i]['ema_200']
            if pd.isna(ema): continue

            direction = "LONG" if price > ema else "SHORT"
            sig = LiveSignal(
                id="baseline", symbol=symbol, timestamp=date,
                entry_price=price,
                target_price=price * (1.05 if direction == "LONG" else 0.95),
                stop_loss_price=price * (0.97 if direction == "LONG" else 1.03),
                direction=direction, status="WAITING_FOR_ENTRY", conviction=100, rating="BUY", timeframe="SWING"
            )
            outcome = OutcomeEngine.evaluate_outcome(sig, df.iloc[i+1 : i+21])
            if outcome["status"] in ["TARGET_HIT", "STOP_LOSS"]:
                ema_trades.append(outcome["status"] == "TARGET_HIT")

        ema_wr = np.mean(ema_trades) * 100 if ema_trades else 0

        results.append({
            "symbol": symbol,
            "bh_return": bh_ret,
            "ema_win_rate": ema_wr,
            "ema_trades": len(ema_trades)
        })

    res_df = pd.DataFrame(results)
    print("\n[Baseline Results]")
    print(res_df)

    os.makedirs("validation/results", exist_ok=True)
    res_df.to_markdown("validation/results/BASELINE_COMPARISON.md")

if __name__ == "__main__":
    import asyncio
    asyncio.run(run_baselines())
