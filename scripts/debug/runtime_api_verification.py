import requests
import json
from collections import Counter

def verify_api():
    base_url = "https://trademind-api-m8jg.onrender.com/api/v1"
    signals_url = f"{base_url}/equity/signals"

    print(f"Calling Production API: {signals_url}")
    try:
        resp = requests.get(signals_url, timeout=15)
        print(f"HTTP Status: {resp.status_code}")

        if resp.status_code != 200:
            print(f"FAIL: API returned {resp.status_code}")
            return

        signals = resp.json()
        print(f"Actual Signal Count: {len(signals)}")

        if len(signals) == 0:
            print("FAIL: API returned zero signals.")
            return

        # Reconcile counts
        horizons = Counter([s.get('timeframe') for s in signals])
        qualities = Counter([s.get('quality_class') for s in signals])

        print("\nReconciliation Metrics:")
        print(f"   Unique Signal IDs: {len(set(s.get('id') for s in signals))}")
        print(f"   Unique Symbols: {len(set(s.get('symbol') for s in signals))}")
        print(f"   SWING Count: {horizons.get('SWING', 0)}")
        print(f"   SHORT Count: {horizons.get('SHORT', 0)}")
        print(f"   LONG Count: {horizons.get('LONG', 0)}")

        print("\nQuality Distribution:")
        for q, count in qualities.items():
            print(f"   {q}: {count}")

        # Field validation for the first 5 signals
        print("\nField Validation (First 5):")
        required_fields = [
            'id', 'symbol', 'timeframe', 'direction', 'entry_price',
            'target_price', 'stop_price', 'current_price',
            'calibrated_probability', 'expected_value', 'risk_reward_ratio',
            'status', 'created_at', 'data_timestamp', 'quality_class'
        ]

        for i, s in enumerate(signals[:5]):
            missing = [f for f in required_fields if f not in s or s[f] is None]
            print(f"   Signal {s.get('id')} ({s.get('symbol')}): {'PASS' if not missing else 'FAIL (Missing: ' + ', '.join(missing) + ')'}")
            if i == 0:
                print(f"      Sample: {json.dumps(s, indent=2)}")

        # Check other endpoints
        accuracy_url = f"{base_url}/equity/accuracy"
        perf_url = f"{base_url}/equity/performance"
        market_url = f"{base_url}/equity/market"

        for url in [accuracy_url, perf_url, market_url]:
            r = requests.get(url, timeout=10)
            print(f"\nEndpoint {url}: {r.status_code}")
            if r.status_code == 200:
                print(f"   Schema keys: {list(r.json().keys())}")

    except Exception as e:
        print(f"CRITICAL ERROR: {e}")

if __name__ == "__main__":
    verify_api()
