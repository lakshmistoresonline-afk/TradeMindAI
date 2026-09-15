import requests
import json
from collections import Counter

def audit():
    url = "https://trademind-api-m8jg.onrender.com/api/v1/equity/signals"
    resp = requests.get(url)
    signals = resp.json()

    print(f"Total signals: {len(signals)}")

    dir_counts = Counter([s.get('direction') for s in signals])
    hor_counts = Counter([s.get('timeframe') for s in signals])
    # Frontend derived quality class logic
    qual_counts = Counter([
        s.get('quality_class') or ('PRIMARY' if s.get('timeframe') == 'SWING' else 'SELECTIVE' if s.get('timeframe') == 'LONG' else 'EXPERIMENTAL')
        for s in signals
    ])

    print("\nDirection Counts:")
    for k, v in dir_counts.items(): print(f"   {k}: {v}")

    print("\nHorizon Counts:")
    for k, v in hor_counts.items(): print(f"   {k}: {v}")

    print("\nQuality Counts (Effective):")
    for k, v in qual_counts.items(): print(f"   {k}: {v}")

    print("\nHorizon x Quality Matrix:")
    matrix = Counter([(s.get('timeframe'), s.get('quality_class') or ('PRIMARY' if s.get('timeframe') == 'SWING' else 'SELECTIVE' if s.get('timeframe') == 'LONG' else 'EXPERIMENTAL')) for s in signals])
    for k, v in matrix.items():
        print(f"   {k[0]} x {k[1]}: {v}")

    # Verify ID match for Dashboard and Signals
    # (Simulated since I can't run a real browser here, but I can check the logic)
    print("\nUI Filter Logic Verification:")
    swing_primary = [s for s in signals if s.get('timeframe') == 'SWING'] # Frontend treats all SWING as PRIMARY in fallback
    print(f"   Dashboard PRIMARY SWING expected: {len(swing_primary)}")
    short_exp = [s for s in signals if s.get('timeframe') == 'SHORT']
    print(f"   Dashboard EXPERIMENTAL SHORT expected: {len(short_exp)}")
    long_sel = [s for s in signals if s.get('timeframe') == 'LONG']
    print(f"   Dashboard SELECTIVE LONG expected: {len(long_sel)}")

if __name__ == "__main__":
    audit()
