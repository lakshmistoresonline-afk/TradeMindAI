
import json
import os

def audit():
    results_path = 'docs/STEP4_FULL_REALIZED_BACKTEST_RESULTS.json'
    with open(results_path, 'r') as f:
        data = json.load(f)

    triggered_expired = [r for r in data['results'] if r['outcome'] == 'EXPIRED' and r['holding_period'] > 1]
    print(f"Triggered EXPIRED trades: {len(triggered_expired)}")
    for t in triggered_expired:
        print(t)

if __name__ == "__main__":
    audit()
