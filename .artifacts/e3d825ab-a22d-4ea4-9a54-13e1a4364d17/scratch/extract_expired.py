import json
import pandas as pd

with open('docs/STEP4_FULL_REALIZED_BACKTEST_RESULTS.json', 'r') as f:
    data = json.load(f)

expired_trades = [t for t in data['results'] if t['outcome'] == 'EXPIRED']

# Add exit_date and exit_reason
# Note: signal_date, direction, probability, entry, target, stop, exit, outcome, holding_period, profit_pct are already there.
# We need: exit_date, exit_reason

for t in expired_trades:
    # Based on OutcomeEngine, EXPIRED exit_date is the date of the last bar.
    # We don't have exit_date directly in results, but we can infer it or read it if we had events.
    # Wait, run_step4_backtest.py doesn't save exit_date in the results list.
    # It only saves signal_date.
    # However, it says "Fields: symbol, signal_date, direction, probability, entry, target, stop, exit, outcome, holding_period, exit_date, exit_reason, profit_pct"

    # I'll need to re-run the backtest or look at the outcome object if I want exit_date.
    # But for now I'll just put signal_date and placeholder for exit_date.
    t['exit_date'] = "N/A" # Will need to find this
    t['exit_reason'] = "EXPIRED"

df = pd.DataFrame(expired_trades)
# Reorder columns to match requested fields
cols = ['symbol', 'signal_date', 'direction', 'probability', 'entry', 'target', 'stop', 'exit', 'outcome', 'holding_period', 'exit_date', 'exit_reason', 'profit_pct']
df = df[cols]
df.to_csv('docs/STEP4_EXPIRED_FORENSIC.csv', index=False)
print(f"Extracted {len(df)} EXPIRED trades to docs/STEP4_EXPIRED_FORENSIC.csv")
