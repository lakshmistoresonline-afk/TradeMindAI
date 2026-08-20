import os
import sys
import asyncio
import pandas as pd
import numpy as np
import json
from datetime import datetime
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '.')))
load_dotenv('backend/.env')
os.environ["TRADEMIND_EXECUTION_MODE"] = "local"

from backend.core.container import container
from backend.services.outcome_engine import OutcomeEngine
from backend.domain.models.ios import LiveSignal

async def perform_audit():
    results_path = 'docs/STEP4_FULL_REALIZED_BACKTEST_RESULTS.json'
    with open(results_path, 'r') as f:
        data = json.load(f)

    expired_results = [t for t in data['results'] if t['outcome'] == 'EXPIRED']
    print(f"Starting forensic audit of {len(expired_results)} EXPIRED trades...")

    audit_records = []

    for t in expired_results:
        symbol = t['symbol']
        signal_date = pd.to_datetime(t['signal_date'])

        prices = await container.repository.get_recent_prices(symbol, limit=5000)
        df = pd.DataFrame([p.model_dump() for p in prices])
        df.set_index('date', inplace=True)
        df.sort_index(inplace=True)
        df.columns = [c.capitalize() for c in df.columns]

        try:
            sig_idx = df.index.get_indexer([signal_date], method='nearest')[0]

            # 1. HOLDING PERIOD & DATES VERIFICATION
            entry_idx = sig_idx + 1
            max_bars = 200
            expiry_idx = min(sig_idx + max_bars, len(df) - 1)

            # Check for data gaps (Corporate Actions)
            subset = df.iloc[sig_idx:expiry_idx+1]
            returns = subset['Close'].pct_change().dropna()
            extreme_gap = returns[abs(returns) > 0.20]

            # 2. STOP ENFORCEMENT CHECK
            direction = t['direction']
            entry_price = t['entry']
            stop_price = t['stop']

            stop_breached_at = None
            for i in range(entry_idx, expiry_idx + 1):
                row = df.iloc[i]
                if direction == "LONG":
                    if row['Low'] <= stop_price:
                        stop_breached_at = df.index[i]
                        break
                else: # SHORT
                    if row['High'] >= stop_price:
                        stop_breached_at = df.index[i]
                        break

            # 3. ENTRY TRIGGER CHECK (Gaps)
            triggered_at = None
            for i in range(entry_idx, expiry_idx + 1):
                row = df.iloc[i]
                low, high = row['Low'], row['High']
                if direction == "LONG":
                    if low <= entry_price <= high or low > entry_price:
                        triggered_at = df.index[i]
                        break
                else:
                    if low <= entry_price <= high or high < entry_price:
                        triggered_at = df.index[i]
                        break

            # 4. FORMULA VERIFICATION (SHORT)
            exit_price = df.iloc[expiry_idx]['Close']
            if direction == "LONG":
                calc_profit = ((exit_price - entry_price) / entry_price) * 100
            else:
                calc_profit = ((entry_price - exit_price) / entry_price) * 100

            audit_records.append({
                "symbol": symbol,
                "signal_date": t['signal_date'],
                "direction": direction,
                "entry": entry_price,
                "stop": stop_price,
                "exit": exit_price,
                "raw_profit": calc_profit,
                "stop_breached": stop_breached_at.isoformat() if stop_breached_at else "NO",
                "triggered_at": triggered_at.isoformat() if triggered_at else "NO",
                "bars_available": expiry_idx - sig_idx,
                "extreme_gap_count": len(extreme_gap),
                "first_gap_pct": extreme_gap.iloc[0]*100 if len(extreme_gap) > 0 else 0
            })

        except Exception as e:
            print(f"Error auditing {symbol}: {e}")

    df_audit = pd.DataFrame(audit_records)
    df_audit.to_csv('docs/STEP4_EXPIRED_FORENSIC_AUDIT.csv', index=False)

    # Generate Summary Report Snippet
    print("\n--- AUDIT SUMMARY ---")
    print(f"Total Audited: {len(df_audit)}")
    print(f"Trades that SHOULD have hit STOP: {len(df_audit[df_audit['stop_breached'] != 'NO'])}")
    print(f"Trades with Extreme Gaps (>20%): {len(df_audit[df_audit['extreme_gap_count'] > 0])}")
    print(f"Trades that NEVER triggered entry (corrected logic): {len(df_audit[df_audit['triggered_at'] == 'NO'])}")

    avg_raw_loss = df_audit[df_audit['raw_profit'] < -5]['raw_profit'].mean()
    print(f"Avg Raw Loss in anomalous trades: {avg_raw_loss:.2f}%")

if __name__ == "__main__":
    asyncio.run(perform_audit())
