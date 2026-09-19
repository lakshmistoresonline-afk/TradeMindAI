import os
import sys
import pandas as pd
import numpy as np
import datetime
from datetime import timezone, timedelta
from sqlalchemy import text
from yahooquery import Ticker as YQTicker

# Add project root to path
sys.path.append(os.getcwd())

# Ensure Neon connection
os.environ["ENVIRONMENT"] = "production"
os.environ["SECRET_KEY"] = "A" * 32
os.environ["MARKET_DATA_INGEST_KEY"] = "SECURE_INGEST_KEY_2026"
os.environ["POSTGRES_URL"] = "postgresql://neondb_owner:npg_L5GbM3HeYfry@ep-fancy-mountain-axa35p28-pooler.c-4.us-east-2.aws.neon.tech/neondb?sslmode=require"

from backend.core.postgres import SessionLocal

def get_signal_population():
    db = SessionLocal()
    try:
        # Fetch resolved signals with required columns
        cols = ["id", "symbol", "direction", "status", "entry_price", "stop_price", "target_price", "timestamp", "outcome_timestamp", "realized_mfe", "realized_mae", "strategy_version", "evaluation_mode"]
        query = text(f"""
            SELECT {', '.join(cols)} FROM shadow_signals
            WHERE strategy_version = 'v2.2' AND status IN ('TARGET_HIT', 'STOP_LOSS', 'EXPIRED')
            UNION ALL
            SELECT {', '.join(cols)} FROM live_signals
            WHERE strategy_version = 'v2.2' AND status IN ('TARGET_HIT', 'STOP_LOSS', 'EXPIRED')
        """)
        res = db.execute(query)
        return [dict(row._mapping) for row in res.fetchall()]
    finally:
        db.close()

def run_simulation(signal, history, stop_offset_atr=0, be_trigger_atr=None, trail_trigger_atr=None):
    if history.empty:
        return signal['status']

    entry = signal['entry_price']
    direction = signal['direction'].upper()

    # Assume 1.0 ATR was used if we need to calculate offsets
    # For now, let's just use fixed percentages for simplicity in first pass, or better,
    # try to estimate ATR from history before signal.

    # Simple fixed offset for simulation
    original_stop_dist = abs(entry - signal['stop_price'])
    original_target_dist = abs(signal['target_price'] - entry)

    # In V2.2, SWING is 2.0 ATR stop.
    # So 1.0 ATR = original_stop_dist / 2.0
    atr_unit = original_stop_dist / 2.0

    sim_stop = signal['stop_price']
    if stop_offset_atr != 0:
        if direction == "LONG":
            sim_stop = entry - (original_stop_dist + (stop_offset_atr * atr_unit))
        else:
            sim_stop = entry + (original_stop_dist + (stop_offset_atr * atr_unit))

    target = signal['target_price']
    current_stop = sim_stop
    status = "EXPIRED"
    mfe = 0
    mae = 0

    for ts, row in history.iterrows():
        high, low, close = row['High'], row['Low'], row['Close']

        # Update MFE/MAE
        if direction == "LONG":
            mfe = max(mfe, (high - entry) / entry * 100)
            mae = min(mae, (low - entry) / entry * 100)
        else:
            mfe = max(mfe, (entry - low) / entry * 100)
            mae = min(mae, (entry - high) / entry * 100)

        # Break-even check
        if be_trigger_atr:
            trigger_val = be_trigger_atr * atr_unit
            current_mfe_abs = (mfe / 100.0) * entry
            if current_mfe_abs >= trigger_val:
                current_stop = entry # Move to break-even

        # Exit check
        if direction == "LONG":
            if low <= current_stop: return "STOP_LOSS"
            if high >= target: return "TARGET_HIT"
        else:
            if high >= current_stop: return "STOP_LOSS"
            if low <= target: return "TARGET_HIT"

    return status

async def main():
    population = get_signal_population()
    print(f"[*] Starting Second-Stage Validation for {len(population)} signals.")

    results = []

    for sig in population:
        symbol = f"{sig['symbol']}.NS"
        start = sig['timestamp']
        end = sig['outcome_timestamp'] or datetime.datetime.now()

        # Add buffer to end
        end = end + timedelta(days=2)

        yq = YQTicker(symbol)
        history = yq.history(start=start, end=end)

        if history.empty:
            print(f"   [!] No data for {sig['symbol']}")
            continue

        if isinstance(history.index, pd.MultiIndex):
            history = history.reset_index(level=0, drop=True)

        history.columns = [c.capitalize() for c in history.columns]

        # Baseline
        res_baseline = run_simulation(sig, history)

        # Offset experiments
        res_025 = run_simulation(sig, history, stop_offset_atr=0.25)
        res_050 = run_simulation(sig, history, stop_offset_atr=0.50)
        res_100 = run_simulation(sig, history, stop_offset_atr=1.00)

        # Management experiments
        res_be_10 = run_simulation(sig, history, be_trigger_atr=1.0)
        res_be_15 = run_simulation(sig, history, be_trigger_atr=1.5)

        results.append({
            "id": sig['id'],
            "original": sig['status'],
            "baseline": res_baseline,
            "atr_025": res_025,
            "atr_050": res_050,
            "atr_100": res_100,
            "be_10": res_be_10,
            "be_15": res_be_15
        })

    df = pd.DataFrame(results)
    df.to_csv("reports/COUNTERFACTUAL_SIMULATION_RESULTS.csv", index=False)

    print("\nSimulation Summary:")
    for col in df.columns:
        if col == "id": continue
        print(f"\nExperiment: {col}")
        print(df[col].value_counts())

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
