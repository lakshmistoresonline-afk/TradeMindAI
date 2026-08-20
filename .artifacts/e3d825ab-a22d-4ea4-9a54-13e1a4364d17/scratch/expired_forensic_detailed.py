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

async def run_forensic():
    results_path = 'docs/STEP4_FULL_REALIZED_BACKTEST_RESULTS.json'
    if not os.path.exists(results_path):
        print(f"Error: {results_path} not found.")
        return

    with open(results_path, 'r') as f:
        data = json.load(f)

    expired_results = [t for t in data['results'] if t['outcome'] == 'EXPIRED']
    print(f"Analyzing {len(expired_results)} EXPIRED trades...")

    forensic_data = []

    for t in expired_results:
        symbol = t['symbol']
        signal_date = pd.to_datetime(t['signal_date'])

        # Get prices to re-evaluate
        prices = await container.repository.get_recent_prices(symbol, limit=5000)
        if not prices:
            print(f"Skipping {symbol}: No price data found.")
            continue

        df = pd.DataFrame([p.model_dump() for p in prices])
        df.set_index('date', inplace=True)
        df.sort_index(inplace=True)
        df.columns = [c.capitalize() for c in df.columns]

        # Find signal index
        try:
            # Match exactly or closest
            idx = df.index.get_indexer([signal_date], method='nearest')[0]

            # Reconstruct signal
            signal = LiveSignal(
                id=f"forensic_{symbol}_{idx}",
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
                rating="BUY" # Added missing field
            )

            future_data = df.iloc[idx+1:].copy()
            outcome = OutcomeEngine.evaluate_outcome(signal, future_data)

            # Extract fields for CSV
            events = outcome.get("events", [])
            exit_date = outcome.get("outcome_date")
            exit_reason = outcome.get("status")

            # Calculate RAW profit_pct (ignoring whether it triggered or not, for forensic)
            entry = t['entry']
            exit_price = outcome.get("outcome_price")
            direction = t['direction']

            if entry and exit_price:
                if direction == "LONG":
                    raw_profit_pct = ((exit_price - entry) / entry) * 100
                else:
                    raw_profit_pct = ((entry - exit_price) / entry) * 100
            else:
                raw_profit_pct = 0.0

            forensic_data.append({
                "symbol": symbol,
                "signal_date": t['signal_date'],
                "direction": direction,
                "probability": t['probability'],
                "entry": entry,
                "target": t['target'],
                "stop": t['stop'],
                "exit": exit_price,
                "outcome": exit_reason,
                "holding_period": len(events),
                "exit_date": exit_date.isoformat() if exit_date else "N/A",
                "exit_reason": exit_reason,
                "profit_pct": raw_profit_pct
            })
        except Exception as e:
            print(f"Error processing {symbol} at {t['signal_date']}: {e}")

    if forensic_data:
        df_forensic = pd.DataFrame(forensic_data)
        df_forensic.to_csv('docs/STEP4_EXPIRED_FORENSIC.csv', index=False)
        print(f"Forensic extraction complete. Saved {len(forensic_data)} rows to docs/STEP4_EXPIRED_FORENSIC.csv")
    else:
        print("No forensic data gathered.")

if __name__ == "__main__":
    asyncio.run(run_forensic())
