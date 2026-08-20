import json
import pandas as pd

def audit():
    with open('docs/STEP4_FULL_REALIZED_BACKTEST_RESULTS.json', 'r') as f:
        data = json.load(f)

    results = data['results']
    zero_profit_stops = [t for t in results if t['outcome'] == 'STOP_LOSS' and abs(t['profit_pct']) < 1e-9]

    print(f"Total zero-profit STOP_LOSS cases: {len(zero_profit_stops)}")

    if zero_profit_stops:
        df = pd.DataFrame(zero_profit_stops)
        df.to_csv('docs/STEP4_ZERO_PROFIT_STOP_AUDIT.csv', index=False)
        for t in zero_profit_stops[:5]:
            print(t)
    else:
        # Create empty file to satisfy task requirement if none found
        pd.DataFrame(columns=['symbol', 'signal_date', 'direction']).to_csv('docs/STEP4_ZERO_PROFIT_STOP_AUDIT.csv', index=False)

if __name__ == "__main__":
    audit()
