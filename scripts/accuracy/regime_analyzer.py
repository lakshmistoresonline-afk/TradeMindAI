
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

async def analyze_regimes():
    print("--- MARKET REGIME ANALYSIS ---")

    # Use NIFTY 50 as benchmark
    symbol = "NIFTY"
    prices = await container.provider.fetch_history(symbol, "5y")
    if prices.empty:
        symbol = "^NSEI"
        prices = await container.provider.fetch_history(symbol, "5y")

    if prices.empty:
        print("[!] No benchmark data found.")
        return

    df = prices.copy()
    df.columns = [c.capitalize() for c in df.columns]

    # Indicators for regime
    df['ema_200'] = df['Close'].rolling(200).mean()
    df['returns'] = df['Close'].pct_change()
    df['volatility'] = df['returns'].rolling(20).std() * np.sqrt(252)

    def get_regime(row):
        if pd.isna(row['ema_200']): return "UNKNOWN"

        is_bullish = row['Close'] > row['ema_200']
        is_high_vol = row['volatility'] > df['volatility'].median()

        if is_bullish:
            return "BULLISH_HIGH_VOL" if is_high_vol else "BULLISH_STABLE"
        else:
            return "BEARISH_HIGH_VOL" if is_high_vol else "BEARISH_STABLE"

    df['regime'] = df.apply(get_regime, axis=1)

    print("\n[Regime Distribution]")
    print(df['regime'].value_counts(normalize=True) * 100)

    # Audit Window 1 vs Window 2
    # Window 1: 2026-05-20 to 2026-08-18 (Approx)
    # Window 2: 2026-02-19 to 2026-05-20

    w1_start, w1_end = datetime(2026, 5, 20), datetime(2026, 8, 18)
    w2_start, w2_end = datetime(2026, 2, 19), datetime(2026, 5, 20)

    def print_window_stats(start, end, label):
        mask = (pd.to_datetime(df.index).tz_localize(None) >= pd.Timestamp(start)) & (pd.to_datetime(df.index).tz_localize(None) <= pd.Timestamp(end))
        sub = df[mask]
        if sub.empty: return
        ret = (sub['Close'].iloc[-1] / sub['Close'].iloc[0] - 1) * 100
        vol = sub['volatility'].mean()
        reg = sub['regime'].mode()[0]
        print(f"\n{label} ({start.date()} to {end.date()}):")
        print(f"  Return: {ret:.2f}%")
        print(f"  Avg Volatility: {vol:.2f}")
        print(f"  Dominant Regime: {reg}")

    print_window_stats(w1_start, w1_end, "Window 1 (Failed)")
    print_window_stats(w2_start, w2_end, "Window 2 (Passed)")

if __name__ == "__main__":
    import asyncio
    asyncio.run(analyze_regimes())
