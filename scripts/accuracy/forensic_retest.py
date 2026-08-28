import os
import sys
import asyncio
import pandas as pd
import numpy as np
import json
from datetime import datetime
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')
os.environ["TRADEMIND_EXECUTION_MODE"] = "local"

from backend.core.container import container
from backend.services.outcome_engine import OutcomeEngine
from backend.domain.models.ios import LiveSignal

async def run_forensic_retest():
    # Load the 322 forensic cases
    forensic_path = 'docs/STEP4_EXPIRED_FORENSIC.csv'
    if not os.path.exists(forensic_path):
        print(f"Error: {forensic_path} not found.")
        return

    df_cases = pd.read_csv(forensic_path)
    print(f"Retesting {len(df_cases)} forensic cases...")

    retest_results = []

    for _, t in df_cases.iterrows():
        symbol = t['symbol']
        signal_date = pd.to_datetime(t['signal_date'])

        prices = await container.repository.get_recent_prices(symbol, limit=5000)
        if not prices: continue

        df = pd.DataFrame([p.model_dump() for p in prices])
        df.set_index('date', inplace=True)
        df.sort_index(inplace=True)
        df.columns = [c.capitalize() for c in df.columns]

        try:
            idx = df.index.get_indexer([signal_date], method='nearest')[0]

            signal = LiveSignal(
                id=f"retest_{symbol}_{idx}",
                symbol=symbol, timestamp=df.index[idx],
                direction=t['direction'],
                conviction=t['probability'] * 100,
                raw_probability=t['probability'],
                calibrated_probability=t['probability'],
                entry_price=t['entry'],
                target_price=t['target'],
                stop_loss_price=t['stop'],
                status="WAITING_FOR_ENTRY",
                timeframe="SWING",
                rating="BUY"
            )

            future_data = df.iloc[idx+1:].copy()
            outcome = OutcomeEngine.evaluate_outcome(signal, future_data)

            # Assertions
            status = outcome.get("status")
            actual_entry = outcome.get("actual_entry_price")
            profit = outcome.get("profit_pct", 0.0)

            # 1. Favorable Gap Assertion (for the known ADANIENT cases etc.)
            # If we know the next bar gapped favorably, it MUST have an actual_entry_price.

            # 2. Chronology Assertion
            triggered_at = outcome.get("triggered_at")
            outcome_date = outcome.get("outcome_date")
            if triggered_at and outcome_date:
                assert outcome_date >= triggered_at, f"Outcome date {outcome_date} before entry {triggered_at}"

            retest_results.append({
                "symbol": symbol,
                "signal_date": t['signal_date'],
                "direction": t['direction'],
                "intended_entry": t['entry'],
                "actual_entry": actual_entry,
                "entry_execution_type": outcome.get("entry_execution_type"),
                "target": t['target'],
                "stop": t['stop'],
                "entry_date": triggered_at.isoformat() if triggered_at else "N/A",
                "exit_date": outcome_date.isoformat() if outcome_date else "N/A",
                "outcome": status,
                "bars_to_entry": outcome.get("bars_to_entry"),
                "bars_in_position": outcome.get("bars_in_position"),
                "bars_to_expiry": outcome.get("bars_to_expiry"),
                "profit_pct": profit
            })

        except Exception as e:
            print(f"Error retesting {symbol} at {t['signal_date']}: {e}")

    df_retest = pd.DataFrame(retest_results)
    df_retest.to_csv('docs/STEP4_FORENSIC_RETEST.csv', index=False)

    print("\n--- RETEST SUMMARY ---")
    print(f"Total Retested: {len(df_retest)}")
    print(f"Outcome Distribution:\n{df_retest['outcome'].value_counts()}")

    # Critical Check: Are any still EXPIRED?
    expired = df_retest[df_retest['outcome'] == 'EXPIRED']
    if len(expired) > 0:
        print(f"WARNING: {len(expired)} trades still EXPIRED. Check if they hit stop after fill.")

    # Gap execution check
    gap_fills = df_retest[df_retest['entry_execution_type'] == 'FAVORABLE_GAP']
    print(f"Favorable Gaps Executed: {len(gap_fills)}")

if __name__ == "__main__":
    asyncio.run(run_forensic_retest())
