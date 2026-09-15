import requests
from collections import Counter

def audit():
    url = "https://trademind-api-m8jg.onrender.com/api/v1/equity/signals"
    resp = requests.get(url)
    signals = resp.json()

    ids = [s.get('id') for s in signals]
    id_counts = Counter(ids)
    dupe_ids = [i for i, c in id_counts.items() if c > 1]

    print(f"Total Signals: {len(signals)}")
    print(f"Duplicate IDs: {len(dupe_ids)}")

    # symbol + horizon + timestamp (created_at)
    keys = [(s.get('symbol'), s.get('timeframe'), s.get('created_at')) for s in signals]
    key_counts = Counter(keys)
    dupe_keys = [k for k, c in key_counts.items() if c > 1]
    print(f"Duplicate symbol+horizon+timestamp: {len(dupe_keys)}")

    # prediction IDs
    pids = [s.get('prediction_id') for s in signals if s.get('prediction_id')]
    pid_counts = Counter(pids)
    dupe_pids = [p for p, c in pid_counts.items() if c > 1]
    print(f"Duplicate Prediction IDs: {len(dupe_pids)}")

    # Distribution
    horizons = Counter([s.get('timeframe') for s in signals])
    print(f"\nDistribution:")
    print(f"   SWING: {horizons.get('SWING', 0)}")
    print(f"   SHORT: {horizons.get('SHORT', 0)}")
    print(f"   LONG: {horizons.get('LONG', 0)}")

if __name__ == "__main__":
    audit()
