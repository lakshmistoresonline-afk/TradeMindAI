import requests
from collections import Counter

def reconcile():
    base = "https://trademind-api-m8jg.onrender.com/api/v1"
    active_url = f"{base}/equity/signals"
    history_url = f"{base}/equity/history"

    print("--- RECONCILIATION ---")

    # 1. Active Signals
    try:
        active_resp = requests.get(active_url)
        active_data = active_resp.json()
        print(f"Active Signals Count: {len(active_data)}")

        # Check active distribution
        active_horizons = Counter([s.get('timeframe') for s in active_data])
        print(f"   Active SWING: {active_horizons.get('SWING', 0)}")
        print(f"   Active SHORT: {active_horizons.get('SHORT', 0)}")
        print(f"   Active LONG: {active_horizons.get('LONG', 0)}")
    except Exception as e:
        print(f"Active Error: {e}")

    # 2. Historical Signals
    try:
        history_resp = requests.get(history_url)
        if history_resp.status_code == 200:
            history_data = history_resp.json()
            print(f"Historical Signals Total: {history_data.get('total')}")
            records = history_data.get('records', [])
            print(f"   Fetched Sample Count: {len(records)}")

            history_horizons = Counter([r.get('timeframe') for r in records])
            print(f"   History Sample SWING: {history_horizons.get('SWING', 0)}")
            print(f"   History Sample SHORT: {history_horizons.get('SHORT', 0)}")
        else:
            print(f"History Endpoint Status: {history_resp.status_code}")
    except Exception as e:
        print(f"History Error: {e}")

if __name__ == "__main__":
    reconcile()
